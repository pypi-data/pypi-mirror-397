"""Test Merge Join to understand the duplicate issue."""

import json

# Check how many images each product should have
images_by_product = {}
for line in open('images_3_1k.jsonl'):
    if line.strip():
        img = json.loads(line)
        pid = img['product_id']
        if pid not in images_by_product:
            images_by_product[pid] = []
        images_by_product[pid].append(img)

# Check products with checked=1
products_checked = []
for line in open('products_3_1k.jsonl'):
    if line.strip():
        p = json.loads(line)
        if p.get('checked') == 1:
            products_checked.append(p)

print("Expected rows per product (first 10 products with checked=1):")
for p in products_checked[:10]:
    pid = p['product_id']
    img_count = len(images_by_product.get(pid, []))
    print(f"  Product {pid}: {img_count} images -> should produce {img_count} rows")

# Check actual Merge Join results
print("\nActual Merge Join results (first 10 products):")
merge_results = {}
for line in open('results_1k_1_merge_join_sorted_data.jsonl'):
    if line.strip():
        row = json.loads(line)
        pid = row['product_id']
        if pid not in merge_results:
            merge_results[pid] = []
        merge_results[pid].append(row.get('image') is not None)

for pid in sorted(merge_results.keys())[:10]:
    rows = merge_results[pid]
    with_images = sum(rows)
    without_images = len(rows) - with_images
    expected = len(images_by_product.get(pid, []))
    print(f"  Product {pid}: {len(rows)} rows ({with_images} with images, {without_images} without) - Expected: {expected} rows")







