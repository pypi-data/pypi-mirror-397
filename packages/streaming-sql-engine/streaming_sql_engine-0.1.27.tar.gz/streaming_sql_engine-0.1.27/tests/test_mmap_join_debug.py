"""Simple test for MMAP Join to debug why it returns 510 rows instead of 1,560."""

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

# Test data files (should match benchmark files)
products_file = "products_3.jsonl"
images_file = "images_3.jsonl"

# Check if files exist
if not os.path.exists(products_file):
    print(f"[ERROR] File not found: {products_file}")
    print("Run: python generate_test_data_100k.py")
    sys.exit(1)

if not os.path.exists(images_file):
    print(f"[ERROR] File not found: {images_file}")
    print("Run: python generate_test_data_100k.py")
    sys.exit(1)

print("="*70)
print("MMAP JOIN DEBUG TEST")
print("="*70)
print()

# First, let's check the data
print("1. Checking data files...")
print(f"   Products file: {products_file}")
print(f"   Images file: {images_file}")

# Count products
product_count = 0
product_ids = set()
for row in load_jsonl_file(products_file):
    product_count += 1
    pid = row.get("product_id")
    if pid is not None:
        product_ids.add(pid)
    if product_count <= 3:
        print(f"   Sample product {product_count}: {row}")

print(f"   Total products: {product_count}")
print(f"   Unique product_ids: {len(product_ids)}")
print(f"   Sample product_ids: {sorted(list(product_ids))[:10]}")

# Count images
image_count = 0
image_product_ids = set()
images_by_product = {}
for row in load_jsonl_file(images_file):
    image_count += 1
    pid = row.get("product_id")
    if pid is not None:
        image_product_ids.add(pid)
        if pid not in images_by_product:
            images_by_product[pid] = 0
        images_by_product[pid] += 1
    if image_count <= 3:
        print(f"   Sample image {image_count}: {row}")

print(f"   Total images: {image_count}")
print(f"   Unique product_ids in images: {len(image_product_ids)}")
print(f"   Sample product_ids in images: {sorted(list(image_product_ids))[:10]}")

# Check overlap
overlap = product_ids & image_product_ids
print(f"   Product IDs in both: {len(overlap)}")
print(f"   Sample overlap: {sorted(list(overlap))[:10]}")

# Count expected rows (for products with checked=1)
print()
print("2. Calculating expected results...")
checked_products = 0
expected_rows = 0
for row in load_jsonl_file(products_file):
    if row.get("checked") == 1:
        checked_products += 1
        pid = row.get("product_id")
        if pid in images_by_product:
            expected_rows += images_by_product[pid]
        else:
            expected_rows += 1  # LEFT JOIN: one row with NULL images

print(f"   Products with checked=1: {checked_products}")
print(f"   Expected total rows: {expected_rows}")
print(f"   Expected rows per product (avg): {expected_rows / checked_products if checked_products > 0 else 0:.2f}")

print()
print("="*70)
print("3. Testing MMAP Join (matching benchmark_all_configurations.py)")
print("="*70)

# Create products source with WHERE filter (checked=1) - matching benchmark
def products_source():
    for row in load_jsonl_file(products_file):
        if row.get("checked") == 1:
            yield row

# Create images source
def images_source():
    for row in load_jsonl_file(images_file):
        yield row

# Create ScanIterator for products (like the engine does)
# This prefixes columns with "products."
products_scan = ScanIterator(
    products_source,
    "products",
    "products",
    required_columns=None,  # All columns
    debug=False
)

# Test: Get first row from scan to see its structure
print("\n3a. Testing ScanIterator output...")
try:
    first_scan_row = next(products_scan)
    print(f"   First scan row keys: {list(first_scan_row.keys())[:10]}")
    print(f"   Has 'products.product_id': {'products.product_id' in first_scan_row}")
    print(f"   Has 'product_id': {'product_id' in first_scan_row}")
    print(f"   products.product_id value: {first_scan_row.get('products.product_id')}")
except Exception as e:
    print(f"   ERROR getting first scan row: {e}")
    import traceback
    traceback.print_exc()

# Recreate scan iterator for the join
products_scan_for_join = ScanIterator(
    products_source,
    "products",
    "products",
    required_columns=None,
    debug=False
)

# Create MMAP Join (same config as benchmark)
print("\n3b. Creating MMAP Join...")
mmap_join = MmapLookupJoinIterator(
    products_scan_for_join,
    partial(load_jsonl_file, images_file),
    "products.product_id",  # Left key
    "images.product_id",    # Right key
    "LEFT",
    "images",
    "images",
    right_table_filename=images_file,
    required_columns={'image', 'image_type', 'product_id'},  # From optimizer
    debug=True
)

print(f"\nMMAP Join initialized:")
print(f"  left_key: {mmap_join.left_key}")
print(f"  right_key: {mmap_join.right_key}")
print(f"  right_table_col: {mmap_join.right_table_col}")
print(f"  required_columns: {mmap_join.required_columns}")
print(f"  mmap_index exists: {mmap_join.mmap_index is not None}")

if mmap_join.mmap_index:
    print(f"  mmap_index.key_column: {mmap_join.mmap_index.key_column}")
    print(f"  mmap_index position_index size: {len(mmap_join.mmap_index.position_index)} unique keys")
    sample_keys = list(mmap_join.mmap_index.position_index.keys())[:5]
    print(f"  Sample keys in index: {sample_keys}")
    for key in sample_keys[:3]:
        positions = mmap_join.mmap_index.get_positions(key)
        print(f"    Key {key} (type: {type(key).__name__}): {len(positions)} positions")

print()
print("4. Testing join iteration...")
print("-"*70)

row_count = 0
rows_with_images = 0
rows_without_images = 0
products_seen = {}
first_few_rows = []
exceptions_caught = []

try:
    for row in mmap_join:
        row_count += 1
        
        # Extract product_id
        pid = row.get("product_id") or row.get("products.product_id")
        
        # Extract image
        img = row.get("image") or row.get("images.image")
        
        if img:
            rows_with_images += 1
        else:
            rows_without_images += 1
        
        # Track products
        if pid not in products_seen:
            products_seen[pid] = {"total": 0, "with_images": 0, "without_images": 0}
        products_seen[pid]["total"] += 1
        if img:
            products_seen[pid]["with_images"] += 1
        else:
            products_seen[pid]["without_images"] += 1
        
        # Store first few rows
        if len(first_few_rows) < 5:
            first_few_rows.append({
                "product_id": pid,
                "image": img,
                "row_keys": list(row.keys())
            })
        
        # Limit output for large datasets
        if row_count >= 1000000:
            print(f"  [INFO] Capped at 1M rows for testing")
            break
except Exception as e:
    exceptions_caught.append(str(e))
    print(f"\n  [ERROR] Exception during iteration: {e}")
    import traceback
    traceback.print_exc()

print(f"\nResults:")
print(f"  Total rows: {row_count:,}")
print(f"  Rows with images: {rows_with_images:,}")
print(f"  Rows without images: {rows_without_images:,}")
print(f"  Unique products: {len(products_seen)}")
print(f"  Expected rows: {expected_rows:,}")

print(f"\nFirst 5 rows:")
for i, r in enumerate(first_few_rows, 1):
    print(f"  Row {i}: product_id={r['product_id']}, image={'HAS IMAGE' if r['image'] else 'NULL'}, keys={r['row_keys'][:5]}")

print(f"\nSample products breakdown:")
for pid in sorted(products_seen.keys())[:10]:
    info = products_seen[pid]
    expected = images_by_product.get(pid, 0) if pid in images_by_product else 1
    status = "OK" if info["total"] == expected and info["without_images"] == 0 else "ISSUE"
    print(f"  Product {pid}: {info['total']} rows ({info['with_images']} with images, {info['without_images']} without) - Expected: {expected} [{status}]")

# Check for issues
print()
print("="*70)
print("5. Analysis")
print("="*70)

issues = []
if row_count != expected_rows:
    issues.append(f"Row count mismatch: got {row_count:,}, expected {expected_rows:,} (diff: {expected_rows - row_count:,})")

if rows_without_images > 0:
    issues.append(f"Found {rows_without_images:,} rows with NULL images (should be 0 if all products have images)")

# Check if products are getting correct number of rows
for pid in products_seen.keys():
    info = products_seen[pid]
    expected = images_by_product.get(pid, 0) if pid in images_by_product else 1
    if info["total"] != expected:
        issues.append(f"Product {pid}: got {info['total']} rows, expected {expected}")
    if info["without_images"] > 0 and pid in images_by_product:
        issues.append(f"Product {pid}: has {info['without_images']} rows with NULL images (should be 0)")

if exceptions_caught:
    print("\nEXCEPTIONS CAUGHT:")
    for exc in exceptions_caught:
        print(f"  - {exc}")

if issues:
    print("\nISSUES FOUND:")
    for issue in issues[:20]:  # Limit to first 20 issues
        print(f"  - {issue}")
    if len(issues) > 20:
        print(f"  ... and {len(issues) - 20} more issues")
else:
    print("\n✓ ALL TESTS PASSED!")

print()
print("="*70)
print("6. Testing key lookup directly")
print("="*70)

# Test a specific product_id lookup
if mmap_join.mmap_index:
    test_product_id = sorted(list(product_ids))[0] if product_ids else None
    if test_product_id is not None:
        print(f"\nTesting direct lookup for product_id={test_product_id} (type: {type(test_product_id).__name__}):")
        
        # Check if key exists in index
        print(f"  Key in position_index: {test_product_id in mmap_join.mmap_index.position_index}")
        
        # Get positions
        positions = mmap_join.mmap_index.get_positions(test_product_id)
        print(f"  Positions found: {len(positions)}")
        
        # Get rows
        rows = mmap_join.mmap_index.get_rows(test_product_id, required_columns={'image', 'image_type', 'product_id'})
        print(f"  Rows returned: {len(rows)}")
        if rows:
            print(f"  First row: {rows[0]}")
        
        # Test _get_matches
        matches = mmap_join._get_matches(test_product_id)
        print(f"  _get_matches returned: {len(matches)} matches")
        if matches:
            print(f"  First match: {matches[0]}")
            print(f"  First match keys: {list(matches[0].keys())}")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)

