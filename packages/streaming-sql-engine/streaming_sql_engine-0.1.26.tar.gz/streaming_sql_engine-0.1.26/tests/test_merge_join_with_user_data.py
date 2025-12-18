"""
Test Merge Join with the user's actual data format.
"""

import json
from streaming_sql_engine import Engine

def load_jsonl_file(filename):
    """Load JSONL file line by line."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def check_sorted(filename, sort_key):
    """Check if a JSONL file is sorted by the given key."""
    prev_value = None
    line_num = 0
    is_sorted = True
    
    with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                row = json.loads(line)
                current_value = row.get(sort_key)
                
                if prev_value is not None:
                    if current_value < prev_value:
                        print(f"  Line {line_num}: {sort_key}={current_value} < previous {sort_key}={prev_value} (NOT SORTED!)")
                        is_sorted = False
                        break
                
                prev_value = current_value
    
    if is_sorted:
        print(f"  [OK] File is sorted by '{sort_key}' ({line_num} rows checked)")
    else:
        print(f"  [ERROR] File is NOT sorted by '{sort_key}'")
    
    return is_sorted


def main():
    print("=" * 70)
    print("CHECKING IF DATA IS SORTED FOR MERGE JOIN")
    print("=" * 70)
    print()
    
    # Check if files exist
    products_file = "products.jsonl"
    images_file = "images.jsonl"
    
    import os
    if not os.path.exists(products_file):
        print(f"[ERROR] File not found: {products_file}")
        print("Please create products.jsonl with your data")
        return
    
    if not os.path.exists(images_file):
        print(f"[ERROR] File not found: {images_file}")
        print("Please create images.jsonl with your data")
        return
    
    print("Checking products.jsonl:")
    products_sorted = check_sorted(products_file, "product_id")
    print()
    
    print("Checking images.jsonl:")
    images_sorted = check_sorted(images_file, "product_id")
    print()
    
    if not products_sorted or not images_sorted:
        print("=" * 70)
        print("RESULT: Data is NOT sorted. Merge Join will NOT work correctly!")
        print("=" * 70)
        print()
        print("To sort your files, use:")
        print(f"  python examples/sort_jsonl.py {products_file} products_sorted.jsonl product_id")
        print(f"  python examples/sort_jsonl.py {images_file} images_sorted.jsonl product_id")
        print()
        print("OR regenerate the test data:")
        print("  python generate_test_data_1000.py")
        return
    
    print("=" * 70)
    print("RESULT: Data IS sorted! Merge Join will work.")
    print("=" * 70)
    print()
    
    # Test Merge Join
    print("Testing Merge Join with your data...")
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
    
    query = """
        SELECT 
            products.product_id,
            products.product_sku,
            products.title,
            images.image,
            images.image_type
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
        WHERE products.checked = 1
    """
    
    print("Query:")
    print(query)
    print()
    print("Results:")
    print()
    
    results = []
    for row in engine.query(query):
        results.append(row)
        print(f"  {row}")
    
    print()
    print(f"Total rows: {len(results)}")
    print()
    print("[OK] Merge Join worked successfully!")


if __name__ == "__main__":
    main()
