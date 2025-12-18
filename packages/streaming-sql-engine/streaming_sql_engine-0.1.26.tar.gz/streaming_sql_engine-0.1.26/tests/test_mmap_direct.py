"""
Test MMAP index lookup directly to see if it works.
"""

from mmap_index import MmapPositionIndex
import json

print("=" * 70)
print("TESTING MMAP INDEX DIRECTLY")
print("=" * 70)

# Build index
print("\n1. Building MMAP index for images_3.jsonl...")
idx = MmapPositionIndex('images_3.jsonl', 'product_id', debug=False, use_polars=False)

print(f"   Index built: {len(idx)} unique keys, {idx.get_total_rows()} total rows")

# Check first few images
print("\n2. Checking first 5 images from file:")
for i, line in enumerate(open('images_3.jsonl')):
    if i >= 5:
        break
    img = json.loads(line)
    product_id = img.get('product_id')
    print(f"   Image {i+1}: product_id={product_id} (type={type(product_id).__name__})")

# Test lookups
print("\n3. Testing MMAP index lookups:")
test_ids = [1, 2, 3, 4, 5]
for product_id in test_ids:
    rows = idx.get_rows(product_id)
    print(f"   product_id={product_id}: {len(rows)} rows found")
    if rows:
        print(f"      First row keys: {list(rows[0].keys())}")
        print(f"      First row product_id: {rows[0].get('product_id')} (type={type(rows[0].get('product_id')).__name__})")

# Check if index has the keys
print("\n4. Checking index contents:")
print(f"   Sample keys in index: {list(idx.position_index.keys())[:5]}")
print(f"   Key types: {[type(k).__name__ for k in list(idx.position_index.keys())[:5]]}")

# Test with actual product_id from products file
print("\n5. Testing with product_id from products file:")
first_product = json.loads(open('products_3.jsonl').readline())
product_id_from_product = first_product.get('product_id')
print(f"   Product product_id: {product_id_from_product} (type={type(product_id_from_product).__name__})")

rows_from_product = idx.get_rows(product_id_from_product)
print(f"   Lookup result: {len(rows_from_product)} rows")
if rows_from_product:
    print(f"      First row: {rows_from_product[0]}")









