"""
Test MMAP Join with required_columns to see what's happening.
"""

import json
from mmap_index import MmapPositionIndex

print("Testing MMAP index with required_columns...")

idx = MmapPositionIndex("images_3_1k.jsonl", "product_id", debug=False)

# Test without required_columns
print("\n1. Without required_columns:")
rows1 = idx.get_rows(1)
print(f"   Rows: {len(rows1)}")
if rows1:
    print(f"   First row keys: {list(rows1[0].keys())}")

# Test with required_columns (only image and image_type)
print("\n2. With required_columns=['image', 'image_type', 'product_id']:")
rows2 = idx.get_rows(1, required_columns={'image', 'image_type', 'product_id'})
print(f"   Rows: {len(rows2)}")
if rows2:
    print(f"   First row keys: {list(rows2[0].keys())}")
    print(f"   First row: {rows2[0]}")

# Test with required_columns (only product_id - join key)
print("\n3. With required_columns=['product_id']:")
rows3 = idx.get_rows(1, required_columns={'product_id'})
print(f"   Rows: {len(rows3)}")
if rows3:
    print(f"   First row keys: {list(rows3[0].keys())}")







