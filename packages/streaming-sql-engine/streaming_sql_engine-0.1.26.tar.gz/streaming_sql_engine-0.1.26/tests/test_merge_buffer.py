"""Test if Merge Join buffer is being filled correctly."""

import json
from streaming_sql_engine.operators import MergeJoinIterator, ScanIterator
from functools import partial

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

# Check how many images product 1 should have
images_for_1 = [json.loads(line) for line in open('images_3_1k.jsonl') if line.strip() and json.loads(line)['product_id'] == 1]
print(f"Product 1 should have {len(images_for_1)} images")

# Create Merge Join with debug
products_iter = ScanIterator(
    lambda: load_jsonl_file("products_3_1k.jsonl", dynamic_where="products.checked = '1'"),
    "products",
    "products",
    required_columns=None,
    debug=False
)

merge_join = MergeJoinIterator(
    products_iter,
    lambda: load_jsonl_file("images_3_1k.jsonl"),
    "products.product_id",
    "images.product_id",
    "LEFT",
    "images",
    "images",
    debug=True
)

# Enable debug on the merge join
merge_join.debug = True

# Monkey patch to see buffer contents
original_fill = merge_join._fill_right_buffer
def debug_fill_buffer(target_key):
    original_fill(target_key)
    if target_key == 1:
        print(f"  DEBUG: Buffer for product_id=1 has {len(merge_join._right_buffer)} rows")
        if merge_join._right_buffer:
            print(f"  DEBUG: First buffer row keys: {list(merge_join._right_buffer[0].keys())[:5]}")

merge_join._fill_right_buffer = debug_fill_buffer

print("\nExecuting Merge Join (first 5 rows for product 1):")
row_count = 0
product_1_rows = 0
for row in merge_join:
    pid = row.get('product_id') or row.get('products.product_id')
    if pid == 1:
        product_1_rows += 1
        img = row.get('image') or row.get('images.image')
        print(f"  Product 1 Row {product_1_rows}: image={'HAS IMAGE' if img else 'NULL'}")
        if product_1_rows >= 5:
            break
    row_count += 1
    if row_count >= 20:
        break

print(f"\nTotal rows for product 1: {product_1_rows} (expected: {len(images_for_1)})")







