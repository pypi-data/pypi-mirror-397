"""
Test WHERE clause application with 1K data.
"""

import json
from functools import partial
from streaming_sql_engine import Engine

def load_jsonl_file(filename, dynamic_where=None, dynamic_columns=None):
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                if dynamic_where:
                    # Normalize the WHERE clause for easier matching
                    where_lower = dynamic_where.lower().replace(" ", "")
                    
                    # Check for checked=1 patterns (with various formats)
                    if ("checked=1" in where_lower or "checked='1'" in where_lower or 
                        "checked=\"1\"" in where_lower or ".checked=1" in where_lower or
                        ".checked='1'" in where_lower or ".checked=\"1\"" in where_lower):
                        if row.get("checked") != 1:
                            continue
                    # Check for checked=0 patterns
                    elif ("checked=0" in where_lower or "checked='0'" in where_lower or
                          "checked=\"0\"" in where_lower or ".checked=0" in where_lower or
                          ".checked='0'" in where_lower or ".checked=\"0\"" in where_lower):
                        if row.get("checked") != 0:
                            continue
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                yield row

print("Testing WHERE clause with 1K data...")

engine = Engine(debug=False, use_polars=False)

engine.register(
    "products",
    partial(load_jsonl_file, "products_3_1k.jsonl"),
    filename="products_3_1k.jsonl"
)

engine.register(
    "images",
    partial(load_jsonl_file, "images_3_1k.jsonl"),
    filename="images_3_1k.jsonl"
)

query = """
    SELECT 
        products.product_id,
        images.image
    FROM products
    LEFT JOIN images ON products.product_id = images.product_id
    WHERE products.checked = 1
"""

print("\nQuery:")
print(query)

# Count expected
products_checked_1 = sum(1 for line in open("products_3_1k.jsonl") 
                        if line.strip() and json.loads(line).get("checked") == 1)
print(f"\nExpected products with checked=1: {products_checked_1}")

print("\nExecuting query...")
row_count = 0
product_ids = set()
for row in engine.query(query):
    row_count += 1
    product_ids.add(row.get("product_id"))
    if row_count <= 10:
        print(f"  Row {row_count}: product_id={row.get('product_id')}, image={row.get('image')}")

print(f"\nTotal rows: {row_count}")
print(f"Unique product_ids: {len(product_ids)}")
print(f"Expected unique products: {products_checked_1}")

# Check if we got products with checked=0
all_products = {json.loads(line).get("product_id"): json.loads(line).get("checked") 
                for line in open("products_3_1k.jsonl") if line.strip()}
products_with_checked_0 = [pid for pid in product_ids if all_products.get(pid) == 0]
if products_with_checked_0:
    print(f"\nERROR: Found {len(products_with_checked_0)} products with checked=0 in results!")
    print(f"  Examples: {products_with_checked_0[:5]}")








