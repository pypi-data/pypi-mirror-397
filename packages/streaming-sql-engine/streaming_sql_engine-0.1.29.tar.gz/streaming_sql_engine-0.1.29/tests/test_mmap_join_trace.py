"""
Trace MMAP Join execution to see what's happening.
"""

import json
from streaming_sql_engine import Engine

def load_jsonl_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

print("=" * 70)
print("TRACING MMAP JOIN EXECUTION")
print("=" * 70)

# Test MMAP Join
engine = Engine(debug=False, use_polars=False)

engine.register(
    "products",
    lambda: load_jsonl_file("products_3.jsonl"),
    filename="products_3.jsonl"  # This enables MMAP for products
)

engine.register(
    "images",
    lambda: load_jsonl_file("images_3.jsonl"),
    filename="images_3.jsonl"  # This enables MMAP for images
)

query = """
    SELECT 
        products.product_id,
        products.checked,
        images.image
    FROM products
    LEFT JOIN images ON products.product_id = images.product_id
    WHERE products.checked = 1
"""

print("\nQuery:")
print(query)

# Check how many products have checked=1
print("\n1. Checking data:")
products_checked_1 = [json.loads(line) for line in open('products_3.jsonl') if json.loads(line).get('checked') == 1]
print(f"   Products with checked=1: {len(products_checked_1):,}")

# Check first product with checked=1
first_checked_product = products_checked_1[0]
print(f"   First product with checked=1: product_id={first_checked_product.get('product_id')}")

# Check images for that product
images_for_first = [json.loads(line) for line in open('images_3.jsonl') if json.loads(line).get('product_id') == first_checked_product.get('product_id')]
print(f"   Images for product_id={first_checked_product.get('product_id')}: {len(images_for_first)}")

print("\n2. Executing query (first 10 rows):")
row_count = 0
checked_count = 0
null_image_count = 0

for row in engine.query(query):
    row_count += 1
    if row.get('checked') == 1:
        checked_count += 1
    if row.get('image') is None:
        null_image_count += 1
    
    if row_count <= 10:
        print(f"   Row {row_count}: product_id={row.get('product_id')}, checked={row.get('checked')}, image={row.get('image')}")
    
    if row_count >= 100:  # Sample first 100
        break

print(f"\n3. Summary (first 100 rows):")
print(f"   Total rows: {row_count}")
print(f"   Rows with checked=1: {checked_count}")
print(f"   Rows with null images: {null_image_count}")









