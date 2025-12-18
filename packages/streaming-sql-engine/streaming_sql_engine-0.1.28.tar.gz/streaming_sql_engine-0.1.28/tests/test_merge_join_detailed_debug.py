"""
Detailed debug script to trace Merge Join execution step by step.
"""

import json
from streaming_sql_engine import Engine

def load_jsonl_file(filename):
    """Load JSONL file line by line."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    print("=" * 70)
    print("DETAILED DEBUG: Why Merge Join Returns 0 Results")
    print("=" * 70)
    print()
    
    products_file = "products.jsonl"
    images_file = "images.jsonl"
    
    import os
    if not os.path.exists(products_file):
        print(f"[ERROR] File not found: {products_file}")
        return
    
    if not os.path.exists(images_file):
        print(f"[ERROR] File not found: {images_file}")
        return
    
    # Step 1: Show actual data
    print("STEP 1: Examining actual data in files...")
    print()
    
    print("Products (first 5):")
    products_data = []
    with open(products_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            if line.strip():
                product = json.loads(line)
                products_data.append(product)
                print(f"  Line {i+1}: product_id={product.get('product_id')}, checked={product.get('checked')}, title={product.get('title')}")
    print()
    
    print("Images (first 5):")
    images_data = []
    with open(images_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            if line.strip():
                image = json.loads(line)
                images_data.append(image)
                print(f"  Line {i+1}: product_id={image.get('product_id')}, image={image.get('image')}")
    print()
    
    # Step 2: Check if data is sorted
    print("STEP 2: Checking if data is sorted by product_id...")
    print()
    
    def check_sorted(filename, sort_key):
        prev_value = None
        line_num = 0
        is_sorted = True
        issues = []
        
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    row = json.loads(line)
                    current_value = row.get(sort_key)
                    
                    if prev_value is not None:
                        if current_value < prev_value:
                            issues.append(f"Line {line_num}: {sort_key}={current_value} < previous {sort_key}={prev_value}")
                            is_sorted = False
                    
                    prev_value = current_value
        
        if is_sorted:
            print(f"  [OK] {filename} is sorted by '{sort_key}' ({line_num} rows)")
        else:
            print(f"  [ERROR] {filename} is NOT sorted!")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"    - {issue}")
        
        return is_sorted
    
    products_sorted = check_sorted(products_file, "product_id")
    print()
    images_sorted = check_sorted(images_file, "product_id")
    print()
    
    if not products_sorted or not images_sorted:
        print("[STOPPING] Data is not sorted. Merge Join requires sorted data.")
        print("Please sort your files first using:")
        print(f"  python examples/sort_jsonl.py {products_file} products_sorted.jsonl product_id")
        print(f"  python examples/sort_jsonl.py {images_file} images_sorted.jsonl product_id")
        return
    
    # Step 3: Test query step by step
    print("STEP 3: Testing query step by step...")
    print()
    
    engine = Engine(debug=False, use_polars=False)
    
    engine.register(
        "products",
        lambda: load_jsonl_file(products_file),
        ordered_by="product_id"
    )
    
    engine.register(
        "images",
        lambda: load_jsonl_file(images_file),
        ordered_by="product_id"
    )
    
    # Test 1: No WHERE, no JOIN (just products)
    print("Test 1: SELECT products only (no join, no where):")
    query1 = "SELECT products.product_id, products.checked FROM products"
    results1 = list(engine.query(query1))
    print(f"  Results: {len(results1)} rows")
    for r in results1[:3]:
        print(f"    {r}")
    print()
    
    # Test 2: WHERE clause only
    print("Test 2: SELECT products WHERE checked=0:")
    query2 = "SELECT products.product_id, products.checked FROM products WHERE products.checked = 0"
    results2 = list(engine.query(query2))
    print(f"  Results: {len(results2)} rows")
    for r in results2[:3]:
        print(f"    {r}")
    print()
    
    # Test 3: JOIN without WHERE
    print("Test 3: JOIN without WHERE clause:")
    query3 = """
        SELECT products.product_id, products.checked, images.image
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
    """
    results3 = []
    try:
        for i, row in enumerate(engine.query(query3)):
            results3.append(row)
            if i < 3:
                print(f"    {row}")
        print(f"  Results: {len(results3)} rows")
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
    print()
    
    # Test 4: JOIN with WHERE
    print("Test 4: JOIN with WHERE products.checked=0:")
    query4 = """
        SELECT products.product_id, products.product_sku, products.title, images.image, images.image_type
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
        WHERE products.checked = 0
    """
    results4 = []
    try:
        for i, row in enumerate(engine.query(query4)):
            results4.append(row)
            if i < 3:
                print(f"    {row}")
        print(f"  Results: {len(results4)} rows")
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
    print()
    
    # Step 4: Manual join simulation
    print("STEP 4: Manual join simulation (to verify data matches)...")
    print()
    
    # Find products with checked=0
    products_checked_0 = [p for p in products_data if p.get('checked') == 0]
    print(f"Products with checked=0: {len(products_checked_0)}")
    for p in products_checked_0[:3]:
        print(f"  product_id={p.get('product_id')}")
    print()
    
    # Find matching images
    product_ids_checked_0 = {p.get('product_id') for p in products_checked_0}
    matching_images = [img for img in images_data if img.get('product_id') in product_ids_checked_0]
    print(f"Images matching those products: {len(matching_images)}")
    for img in matching_images[:3]:
        print(f"  product_id={img.get('product_id')}, image={img.get('image')}")
    print()
    
    # Step 5: Diagnosis
    print("=" * 70)
    print("DIAGNOSIS")
    print("=" * 70)
    print()
    
    if len(results2) == 0:
        print("[ISSUE 1] WHERE clause filters out all products!")
        print(f"  - Found {len(results1)} products total")
        print(f"  - Found {len(results2)} products with checked=0")
        print("  - This means no products have checked=0 in your data")
        print()
        print("  Check your data - maybe checked values are different?")
        checked_values = set(p.get('checked') for p in products_data)
        print(f"  Actual checked values in first 5 products: {checked_values}")
    elif len(results3) == 0:
        print("[ISSUE 2] JOIN is not working!")
        print("  - Products query works")
        print("  - But JOIN returns 0 results")
        print("  - This suggests a join key mismatch or ProjectIterator issue")
    elif len(results4) == 0:
        print("[ISSUE 3] WHERE + JOIN combination fails!")
        print(f"  - JOIN without WHERE: {len(results3)} results")
        print(f"  - JOIN with WHERE checked=0: {len(results4)} results")
        print("  - This suggests WHERE is filtering after join, removing all results")
    else:
        print(f"[OK] Everything works!")
        print(f"  - Products with checked=0: {len(results2)}")
        print(f"  - JOIN results: {len(results4)}")


if __name__ == "__main__":
    main()










