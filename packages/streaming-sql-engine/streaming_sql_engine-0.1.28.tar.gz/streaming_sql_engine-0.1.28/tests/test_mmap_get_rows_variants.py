"""Test MMAP index get_rows with different required_columns."""

from mmap_index import MmapPositionIndex

idx = MmapPositionIndex('images_3_1k.jsonl', 'product_id', debug=False, use_polars=True)

print("Testing get_rows with different required_columns:")
rows1 = idx.get_rows(1)
print(f'1. Without required_columns: {len(rows1)} rows')
if rows1:
    print(f'   First row keys: {list(rows1[0].keys())[:5]}')

rows2 = idx.get_rows(1, required_columns=None)
print(f'2. With required_columns=None: {len(rows2)} rows')

rows3 = idx.get_rows(1, required_columns={'product_id'})
print(f'3. With required_columns={{"product_id"}}: {len(rows3)} rows')
if rows3:
    print(f'   First row keys: {list(rows3[0].keys())}')

rows4 = idx.get_rows(1, required_columns={'image', 'image_type', 'product_id'})
print(f'4. With required_columns={{"image", "image_type", "product_id"}}: {len(rows4)} rows')
if rows4:
    print(f'   First row: {rows4[0]}')







