"""Test _get_matches directly with MMAP Join."""

from streaming_sql_engine.operators_mmap import MmapLookupJoinIterator
from functools import partial

def load_jsonl_file(filename, dynamic_where=None, dynamic_columns=None):
    # Empty generator for testing
    return
    yield

print("Creating MMAP Join iterator...")
mmap_join = MmapLookupJoinIterator(
    iter([]),  # Empty left source
    partial(load_jsonl_file, 'images_3_1k.jsonl'),
    'products.product_id',
    'images.product_id',
    'LEFT',
    'images',
    'images',
    right_table_filename='images_3_1k.jsonl',
    required_columns={'image', 'image_type', 'product_id'},
    debug=False
)

print(f"MMAP Join created:")
print(f"  right_table_col: {mmap_join.right_table_col}")
print(f"  required_columns: {mmap_join.required_columns}")
print(f"  mmap_index exists: {mmap_join.mmap_index is not None}")

print("\nTesting _get_matches with product_id=1:")
matches = mmap_join._get_matches(1)
print(f"  Matches returned: {len(matches)}")
if matches:
    print(f"  First match: {matches[0]}")
    print(f"  First match keys: {list(matches[0].keys())}")
else:
    print("  ERROR: No matches found!")







