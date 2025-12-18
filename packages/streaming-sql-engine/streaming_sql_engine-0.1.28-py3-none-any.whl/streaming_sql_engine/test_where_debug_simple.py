"""
Simple test to debug WHERE clause evaluation.
"""

import json
import os
import sys
import io

# Fix Windows console encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from streaming_sql_engine import Engine


def load_jsonl_file(filename):
    """Load JSONL file."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    products_file = "products_3_1k.jsonl"
    images_file = "images_3_1k.jsonl"
    
    if not os.path.exists(products_file) or not os.path.exists(images_file):
        print(f"[ERROR] Files not found")
        return
    
    query = """
        SELECT 
            products.product_id,
            products.checked,
            images.image
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
        WHERE products.checked = 1
    """
    
    engine = Engine(debug=True, use_polars=False, first_match_only=False)
    
    engine.register("products", lambda: load_jsonl_file(products_file))
    engine.register("images", lambda: load_jsonl_file(images_file))
    
    print("=" * 70)
    print("Testing WHERE clause evaluation")
    print("=" * 70)
    print()
    
    checked_values = set()
    row_count = 0
    
    try:
        for row in engine.query(query):
            row_count += 1
            checked = row.get("checked")
            checked_values.add(checked)
            
            if row_count <= 10:
                print(f"Row {row_count}: product_id={row.get('product_id')}, checked={checked}, "
                      f"has_image={row.get('image') is not None}")
                print(f"  All keys in row: {list(row.keys())}")
            
            if row_count >= 20:
                break
        
        print()
        print(f"Total rows checked: {row_count}")
        print(f"Checked values found: {checked_values}")
        
        if checked_values == {1}:
            print("✅ WHERE clause working correctly!")
        else:
            print(f"❌ WHERE clause NOT working - found {checked_values}, expected {{1}}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
