"""
Test MMAP index directly.
"""

from mmap_index import MmapPositionIndex
import json

print("Building MMAP index for images_3.jsonl...")
index = MmapPositionIndex("images_3.jsonl", "product_id", debug=True, use_polars=False)

print(f"\nIndex built. Unique keys: {len(index)}")
print(f"Total rows indexed: {index.get_total_rows()}")

# Test lookups
print("\nTesting lookups:")
for product_id in [1, 2, 3, 4, 5]:
    rows = index.get_rows(product_id)
    print(f"  product_id={product_id}: {len(rows)} rows")
    if rows:
        print(f"    First row: {rows[0]}")










