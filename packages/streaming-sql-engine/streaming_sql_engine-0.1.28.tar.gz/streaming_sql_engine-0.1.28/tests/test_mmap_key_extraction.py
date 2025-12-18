"""
Test MMAP Join key extraction to see what's happening.
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
                    where_lower = dynamic_where.lower().replace(" ", "")
                    if ("checked=1" in where_lower or "checked='1'" in where_lower or 
                        ".checked=1" in where_lower or ".checked='1'" in where_lower):
                        if row.get("checked") != 1:
                            continue
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                yield row

print("Testing MMAP Join key extraction...")

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

# Check first product with checked=1
first_checked_product = None
for line in open("products_3_1k.jsonl"):
    if line.strip():
        p = json.loads(line)
        if p.get("checked") == 1:
            first_checked_product = p
            break

if first_checked_product:
    print(f"\nFirst product with checked=1: product_id={first_checked_product.get('product_id')}")
    
    # Check images for this product
    images_for_product = [json.loads(line) for line in open("images_3_1k.jsonl") 
                         if json.loads(line).get("product_id") == first_checked_product.get("product_id")]
    print(f"Images for this product: {len(images_for_product)}")
    
    # Test MMAP index lookup
    from mmap_index import MmapPositionIndex
    idx = MmapPositionIndex("images_3_1k.jsonl", "product_id", debug=False)
    rows = idx.get_rows(first_checked_product.get("product_id"))
    print(f"MMAP index lookup for product_id={first_checked_product.get('product_id')}: {len(rows)} rows")

print("\nExecuting query (first 10 rows):")
row_count = 0
for row in engine.query(query):
    row_count += 1
    if row_count <= 10:
        print(f"  Row {row_count}: product_id={row.get('product_id')}, image={row.get('image')}")
    if row_count >= 100:
        break

print(f"\nTotal rows: {row_count}")








