"""Test script to debug WHERE clause filtering issue"""

import json
from streaming_sql_engine import Engine

def load_jsonl_file(filename):
    """Simple JSONL loader without protocol support."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Initialize engine
engine = Engine(debug=True, use_polars=False, first_match_only=False)

# Register sources (without protocol support)
engine.register("products", lambda: load_jsonl_file("products_3_1k.jsonl"))
engine.register("images", lambda: load_jsonl_file("images_3_1k.jsonl"))

# Query with WHERE clause
query = """
    SELECT 
        products.product_id,
        products.product_sku,
        products.title,
        images.image,
        images.image_type
    FROM products
    LEFT JOIN images ON products.product_id = images.product_id
    WHERE products.checked = 1
"""

print("=" * 70)
print("Testing WHERE clause filtering")
print("=" * 70)
print()

# Count products with checked=1
products_checked_1 = sum(
    1 for line in open("products_3_1k.jsonl")
    if line.strip() and json.loads(line).get("checked") == 1
)
print(f"Expected: {products_checked_1} products with checked=1")
print()

# Execute query
row_count = 0
unique_products = set()
for row in engine.query(query):
    row_count += 1
    unique_products.add(row.get("product_id"))
    if row_count <= 5:
        print(f"Row {row_count}: product_id={row.get('product_id')}, checked={row.get('checked', 'N/A')}")

print()
print(f"Results:")
print(f"  Total rows: {row_count}")
print(f"  Unique products: {len(unique_products)}")
print(f"  Expected products: {products_checked_1}")
print()

if row_count == 0:
    print("ERROR: No rows returned!")
elif len(unique_products) != products_checked_1:
    print(f"WARNING: Expected {products_checked_1} unique products, got {len(unique_products)}")
else:
    print("SUCCESS: WHERE clause is working correctly!")
