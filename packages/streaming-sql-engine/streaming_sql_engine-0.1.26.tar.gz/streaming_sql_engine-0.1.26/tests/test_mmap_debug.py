"""
Debug MMAP Join to see why it's not finding matches.
"""

import json
from streaming_sql_engine import Engine

def load_jsonl_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Test MMAP Join with debug
print("Testing MMAP Join...")
engine = Engine(debug=False, use_polars=False)

engine.register(
    "products",
    lambda: load_jsonl_file("products_3.jsonl"),
    filename="products_3.jsonl"
)

engine.register(
    "images",
    lambda: load_jsonl_file("images_3.jsonl"),
    filename="images_3.jsonl"
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
print("\nFirst 10 rows:")

row_count = 0
for row in engine.query(query):
    row_count += 1
    print(f"Row {row_count}: product_id={row.get('product_id')}, checked={row.get('checked')}, image={row.get('image')}")
    if row_count >= 10:
        break

print(f"\nTotal rows returned (first 10 shown): {row_count}")









