"""Simple test for MMAP Join to debug the issue."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from functools import partial
from streaming_sql_engine.operators_mmap import MmapLookupJoinIterator
from streaming_sql_engine.operators import ScanIterator

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

print("Testing MMAP Join with 1K data...")

# Create scan iterator for products
products_iter = ScanIterator(
    lambda: load_jsonl_file("products_3_1k.jsonl", dynamic_where="products.checked = '1'"),
    "products",
    "products",
    required_columns=None,
    debug=False
)

# Get first product row
first_row = next(products_iter)
print(f"\nFirst product row:")
print(f"  Keys: {list(first_row.keys())[:10]}")
print(f"  product_id key options:")
print(f"    'products.product_id': {first_row.get('products.product_id')}")
print(f"    'product_id': {first_row.get('product_id')}")

# Create MMAP Join
mmap_join = MmapLookupJoinIterator(
    iter([first_row]),  # Single row iterator for testing
    partial(load_jsonl_file, "images_3_1k.jsonl"),
    "products.product_id",
    "images.product_id",
    "LEFT",
    "images",
    "images",
    right_table_filename="images_3_1k.jsonl",
    required_columns={'image', 'image_type', 'product_id'},
    debug=True
)

print(f"\nMMAP Join initialized:")
print(f"  left_key: {mmap_join.left_key}")
print(f"  right_key: {mmap_join.right_key}")
print(f"  right_table_col: {mmap_join.right_table_col}")
print(f"  required_columns: {mmap_join.required_columns}")
print(f"  mmap_index exists: {mmap_join.mmap_index is not None}")

# Test key extraction
try:
    key_value = mmap_join._get_key_value(first_row, mmap_join.left_key)
    print(f"\nExtracted key_value: {key_value} (type: {type(key_value).__name__})")
except Exception as e:
    print(f"\nERROR extracting key: {e}")

# Test _get_matches directly
if mmap_join.mmap_index:
    test_key = first_row.get('products.product_id') or first_row.get('product_id')
    print(f"\nTesting _get_matches with key={test_key}:")
    matches = mmap_join._get_matches(test_key)
    print(f"  Matches returned: {len(matches)}")
    if matches:
        print(f"  First match: {matches[0]}")
    else:
        print(f"  ERROR: No matches found!")

# Test MMAP index directly
if mmap_join.mmap_index:
    test_key = first_row.get('products.product_id') or first_row.get('product_id')
    print(f"\nTesting MMAP index directly with key={test_key} (type: {type(test_key).__name__}):")
    print(f"  Index key_column: {mmap_join.mmap_index.key_column}")
    print(f"  Index position_index keys sample: {list(mmap_join.mmap_index.position_index.keys())[:10]}")
    print(f"  Key {test_key} in position_index: {test_key in mmap_join.mmap_index.position_index}")
    positions = mmap_join.mmap_index.get_positions(test_key)
    print(f"  Positions: {positions}")
    rows = mmap_join.mmap_index.get_rows(test_key, required_columns={'image', 'image_type', 'product_id'})
    print(f"  Rows from index: {len(rows)}")
    if rows:
        print(f"  First row: {rows[0]}")
    else:
        print(f"  ERROR: get_rows returned empty even though positions={positions}")

# Test full join iteration
print(f"\nTesting full join iteration:")
mmap_join_full = MmapLookupJoinIterator(
    products_iter,
    partial(load_jsonl_file, "images_3_1k.jsonl"),
    "products.product_id",
    "images.product_id",
    "LEFT",
    "images",
    "images",
    right_table_filename="images_3_1k.jsonl",
    required_columns={'image', 'image_type', 'product_id'},
    debug=True
)

row_count = 0
for row in mmap_join_full:
    row_count += 1
    if row_count <= 5:
        pid = row.get("product_id") or row.get("products.product_id")
        img = row.get("image") or row.get("images.image")
        print(f"  Row {row_count}: product_id={pid}, image={'HAS IMAGE' if img else 'NULL'}")
    if row_count >= 10:
        break

print(f"\nTotal rows: {row_count}")






