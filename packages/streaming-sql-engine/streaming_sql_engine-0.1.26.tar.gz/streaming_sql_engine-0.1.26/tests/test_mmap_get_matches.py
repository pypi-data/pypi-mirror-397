"""
Test _get_matches directly.
"""

import json
from streaming_sql_engine.operators_mmap import MmapLookupJoinIterator
from functools import partial

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

print("Testing _get_matches directly...")

# Create MMAP Join iterator
mmap_join = MmapLookupJoinIterator(
    iter([]),  # Empty left source for now
    partial(load_jsonl_file, "images_3_1k.jsonl"),
    "products.product_id",
    "images.product_id",
    "LEFT",
    "images",
    "images",
    right_table_filename="images_3_1k.jsonl",
    required_columns={'image', 'image_type', 'product_id'},  # From optimizer
    debug=True
)

print(f"\nMMAP Join initialized:")
print(f"  right_table_col: {mmap_join.right_table_col}")
print(f"  required_columns: {mmap_join.required_columns}")
print(f"  mmap_index exists: {mmap_join.mmap_index is not None}")

# Test MMAP index directly
print(f"\nTesting MMAP index directly:")
rows_direct = mmap_join.mmap_index.get_rows(1)
print(f"  Direct get_rows(1): {len(rows_direct)} rows")
if rows_direct:
    print(f"  First row: {rows_direct[0]}")

# Test with required_columns
print(f"\nTesting MMAP index with required_columns:")
required_cols = {'image', 'image_type', 'product_id'}
rows_with_cols = mmap_join.mmap_index.get_rows(1, required_columns=required_cols)
print(f"  get_rows(1, required_columns={required_cols}): {len(rows_with_cols)} rows")
if rows_with_cols:
    print(f"  First row: {rows_with_cols[0]}")

# Test _get_matches directly
print(f"\nTesting _get_matches with product_id=1:")
matches = mmap_join._get_matches(1)
print(f"  Matches returned: {len(matches)}")
if matches:
    print(f"  First match: {matches[0]}")
    print(f"  First match keys: {list(matches[0].keys())}")
else:
    print(f"  ERROR: No matches found!")







