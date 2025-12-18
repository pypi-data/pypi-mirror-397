"""Simple test for MMAP Join - similar to test_merge_join_simple.py"""

import sys
import os
import json
from functools import partial

# Ensure we import from the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streaming_sql_engine.operators_mmap import MmapLookupJoinIterator
from streaming_sql_engine.operators import ScanIterator

def load_jsonl_file(filename):
    """Load JSONL file."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Use actual data files (or create simple test data)
products_file = "products_3.jsonl"
images_file = "images_3.jsonl"

# Check if files exist, if not use simple test data
if not os.path.exists(products_file) or not os.path.exists(images_file):
    print("Data files not found. Using simple test data...")
    
    # Simple test data
    products_data = [
        {"product_id": 1, "name": "Product 1", "checked": 1},
        {"product_id": 2, "name": "Product 2", "checked": 1},
        {"product_id": 3, "name": "Product 3", "checked": 1},
    ]
    
    images_data = [
        {"product_id": 1, "image": "img1_1.jpg"},
        {"product_id": 1, "image": "img1_2.jpg"},
        {"product_id": 1, "image": "img1_3.jpg"},
        {"product_id": 2, "image": "img2_1.jpg"},
        {"product_id": 2, "image": "img2_2.jpg"},
        {"product_id": 3, "image": "img3_1.jpg"},
    ]
    
    def products_source():
        for p in products_data:
            if p.get("checked") == 1:
                yield p
    
    def images_source():
        for img in images_data:
            yield img
    
    # Create ScanIterator for products (like the engine does)
    products_scan = ScanIterator(
        products_source,
        "products",
        "products",
        required_columns=None,
        debug=False
    )
    
    # Create temporary images file for mmap
    import tempfile
    temp_images_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    for img in images_data:
        temp_images_file.write(json.dumps(img) + '\n')
    temp_images_file.close()
    images_file = temp_images_file.name
    
else:
    # Use actual data files with WHERE filter
    def products_source():
        for row in load_jsonl_file(products_file):
            if row.get("checked") == 1:
                yield row
    
    # Create ScanIterator for products (like the engine does)
    products_scan = ScanIterator(
        products_source,
        "products",
        "products",
        required_columns=None,
        debug=False
    )

print("="*60)
print("Testing MMAP Join:")
print("="*60)

# Create MMAP Join
mmap_join = MmapLookupJoinIterator(
    products_scan,
    partial(load_jsonl_file, images_file),
    "products.product_id",  # Left key (with prefix)
    "images.product_id",     # Right key (with prefix)
    "LEFT",
    "images",
    "images",
    right_table_filename=images_file,
    required_columns={'image', 'image_type', 'product_id'},
    debug=True
)

print(f"\nMMAP Join initialized:")
print(f"  left_key: {mmap_join.left_key}")
print(f"  right_key: {mmap_join.right_key}")
print(f"  right_table_col: {mmap_join.right_table_col}")
print(f"  required_columns: {mmap_join.required_columns}")
print(f"  mmap_index exists: {mmap_join.mmap_index is not None}")

if mmap_join.mmap_index:
    print(f"  mmap_index position_index size: {len(mmap_join.mmap_index.position_index)} unique keys")

print("\n" + "="*60)
print("Results:")
print("="*60)

results = []
row_count = 0
for row in mmap_join:
    row_count += 1
    pid = row.get("product_id") or row.get("products.product_id")
    img = row.get("image") or row.get("images.image")
    results.append({"product_id": pid, "image": img})
    
    if row_count <= 10:
        print(f"  Row {row_count}: product_id={pid}, image={'HAS IMAGE' if img else 'NULL'}")

print(f"\nTotal rows: {row_count}")

# Analyze results
print("\nResults by product:")
product_counts = {}
for r in results:
    pid = r["product_id"]
    if pid not in product_counts:
        product_counts[pid] = {"total": 0, "with_images": 0, "without_images": 0}
    product_counts[pid]["total"] += 1
    if r["image"]:
        product_counts[pid]["with_images"] += 1
    else:
        product_counts[pid]["without_images"] += 1

for pid in sorted(product_counts.keys()):
    counts = product_counts[pid]
    status = "OK" if counts["without_images"] == 0 else "ISSUE"
    print(f"  Product {pid}: {counts['total']} rows ({counts['with_images']} with images, {counts['without_images']} without) [{status}]")

# Check for issues
issues = []
for pid in sorted(product_counts.keys()):
    counts = product_counts[pid]
    if counts["without_images"] > 0:
        issues.append(f"Product {pid}: has {counts['without_images']} rows with NULL images (should be 0)")

if issues:
    print("\n" + "="*60)
    print("ISSUES FOUND:")
    print("="*60)
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)

# Cleanup temp file if created
if 'temp_images_file' in locals():
    try:
        os.unlink(images_file)
    except:
        pass

