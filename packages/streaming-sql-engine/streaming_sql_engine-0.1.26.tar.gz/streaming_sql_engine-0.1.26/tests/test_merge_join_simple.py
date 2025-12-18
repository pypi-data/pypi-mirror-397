"""Simple test for Merge Join with hardcoded data."""

import sys
import os
# Ensure we import from the package, not the root operators.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streaming_sql_engine.operators import MergeJoinIterator

# Simple test data: products and images
products_data = [
    {"product_id": 1, "name": "Product 1"},
    {"product_id": 2, "name": "Product 2"},
    {"product_id": 3, "name": "Product 3"},
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
        yield p

def images_source():
    # MergeJoinIterator's _advance_right will prefix the keys automatically
    for img in images_data:
        yield img

print("Test Data:")
print("Products:")
for p in products_data:
    print(f"  {p}")
print("\nImages:")
for img in images_data:
    print(f"  {img}")

print("\nExpected Results:")
print("  Product 1 should produce 3 rows (one per image)")
print("  Product 2 should produce 2 rows (one per image)")
print("  Product 3 should produce 1 row (one per image)")
print("  Total: 6 rows")

print("\n" + "="*60)
print("Testing Merge Join:")
print("="*60)

merge_join = MergeJoinIterator(
    products_source(),
    images_source,
    "product_id",  # Left key (no prefix needed)
    "images.product_id",  # Right key (with prefix)
    "LEFT",
    "images",
    "images",
    debug=True
)

# Ensure debug is enabled
merge_join.debug = True

results = []
row_count = 0
for row in merge_join:
    row_count += 1
    pid = row.get("product_id") or row.get("products.product_id")
    img = row.get("image") or row.get("images.image")
    results.append({"product_id": pid, "image": img})
    print(f"  Row {row_count}: product_id={pid}, image={img}")

print(f"\nTotal rows: {row_count} (expected: 6)")

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
    expected = len([img for img in images_data if img["product_id"] == pid])
    status = "OK" if counts["total"] == expected and counts["without_images"] == 0 else "ISSUE"
    print(f"  Product {pid}: {counts['total']} rows ({counts['with_images']} with images, {counts['without_images']} without) - Expected: {expected} rows [{status}]")

# Check for issues
issues = []
for pid in sorted(product_counts.keys()):
    counts = product_counts[pid]
    expected = len([img for img in images_data if img["product_id"] == pid])
    if counts["total"] != expected:
        issues.append(f"Product {pid}: got {counts['total']} rows, expected {expected}")
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
