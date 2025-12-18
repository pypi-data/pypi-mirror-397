"""Debug Merge Join to see what's happening."""

import json
from functools import partial
from streaming_sql_engine.operators import MergeJoinIterator, ScanIterator

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

print("Testing Merge Join with first product...")

# Create scan iterators
products_iter = ScanIterator(
    lambda: load_jsonl_file("products_3_1k.jsonl", dynamic_where="products.checked = '1'"),
    "products",
    "products",
    required_columns=None,
    debug=False
)

images_iter = ScanIterator(
    lambda: load_jsonl_file("images_3_1k.jsonl"),
    "images",
    "images",
    required_columns=None,
    debug=False
)

# Create Merge Join
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

print("\nExecuting Merge Join (first 10 rows):")
row_count = 0
for row in merge_join:
    row_count += 1
    pid = row.get('product_id') or row.get('products.product_id')
    img = row.get('image') or row.get('images.image')
    print(f"  Row {row_count}: product_id={pid}, image={'HAS IMAGE' if img else 'NULL'}")
    if row_count >= 10:
        break







