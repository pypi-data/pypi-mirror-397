"""Debug WHERE clause issue"""

import json
from streaming_sql_engine import Engine

def load_jsonl_file(filename):
    """Simple JSONL loader without protocol support."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                print(f"Source row columns: {list(row.keys())}")
                print(f"Has 'checked': {'checked' in row}")
                yield row
                break  # Just first row for debugging

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

print("Executing query...")
print()

row_count = 0
for row in engine.query(query):
    row_count += 1
    print(f"Result row {row_count} columns: {list(row.keys())}")
    print(f"Has 'checked': {'checked' in row or 'products.checked' in row}")
    if row_count >= 3:
        break

print(f"\nTotal rows returned: {row_count}")
