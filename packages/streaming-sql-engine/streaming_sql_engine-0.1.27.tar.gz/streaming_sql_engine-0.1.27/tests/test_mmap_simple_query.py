"""
Test MMAP Join with a simple query to see what's happening.
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
                    checked_1_patterns = ["checked=1", "checked='1'", "checked=\"1\"", ".checked=1", ".checked='1'", ".checked=\"1\""]
                    if any(pattern in where_lower for pattern in checked_1_patterns):
                        if row.get("checked") != 1:
                            continue
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                yield row

print("Testing MMAP Join with simple query...")

engine = Engine(debug=False, use_polars=False)  # use_polars=False enables MMAP

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

print("\nExecuting query (first 5 rows):")
row_count = 0
for row in engine.query(query):
    row_count += 1
    if row_count <= 5:
        print(f"  Row {row_count}: product_id={row.get('product_id')}, image={row.get('image')}")
    if row_count >= 10:
        break

print(f"\nTotal rows: {row_count}")







