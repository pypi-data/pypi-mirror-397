"""
Test if WHERE pushdown is working for MMAP Join configuration.
"""

import json
import inspect
from streaming_sql_engine import Engine

def load_jsonl_file(filename, dynamic_where=None, dynamic_columns=None):
    """Load JSONL with protocol support."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                if dynamic_where:
                    if "checked = 1" in dynamic_where or "checked=1" in dynamic_where:
                        if row.get("checked") != 1:
                            continue
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                yield row

print("=" * 70)
print("TESTING WHERE PUSHDOWN FOR MMAP JOIN")
print("=" * 70)

# Test 1: Check if lambda wrapper breaks protocol detection
print("\n1. Testing protocol detection:")
products_fn = lambda: load_jsonl_file("products_3.jsonl")
print(f"   Lambda signature: {inspect.signature(products_fn)}")

# Direct function
print(f"   Direct function signature: {inspect.signature(load_jsonl_file)}")

# Test 2: Register and query
print("\n2. Registering sources and executing query:")
engine = Engine(debug=False, use_polars=False)

# Register with lambda (like benchmark does)
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
        images.image
    FROM products
    LEFT JOIN images ON products.product_id = images.product_id
    WHERE products.checked = 1
"""

print("\n3. Executing query (first 10 rows):")
row_count = 0
for row in engine.query(query):
    row_count += 1
    if row_count <= 10:
        print(f"   Row {row_count}: product_id={row.get('product_id')}, image={row.get('image')}")
    if row_count >= 100:
        break

print(f"\n4. Total rows returned: {row_count}")
print(f"   Expected: ~50,089 products with checked=1")
print(f"   Expected with images: ~150,048 rows")









