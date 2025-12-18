"""Test MMAP index lookup."""

from mmap_index import MmapPositionIndex
import json

print("Building MMAP index...")
idx = MmapPositionIndex('images_3.jsonl', 'product_id', debug=True)

print(f'\nIndex has {len(idx)} unique keys')
print(f'Total rows: {idx.get_total_rows()}')

# Check first image
first_img = json.loads(open('images_3.jsonl').readline())
print(f'\nFirst image row: product_id={first_img.get("product_id")}, type={type(first_img.get("product_id"))}')

# Try lookup
product_id = first_img.get('product_id')
rows = idx.get_rows(product_id)
print(f'\nLookup for product_id={product_id} (type={type(product_id)}): {len(rows)} rows')
if rows:
    print(f'  First row: {rows[0]}')

# Try lookup with int
rows_int = idx.get_rows(int(product_id))
print(f'\nLookup for product_id={int(product_id)} (type=int): {len(rows_int)} rows')
if rows_int:
    print(f'  First row: {rows_int[0]}')









