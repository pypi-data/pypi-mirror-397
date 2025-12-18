"""
Test Polars join with WHERE clause to see what's happening.
"""

import json
import os
import sys
import io

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
    
    print("=" * 70)
    print("Testing Polars Join with WHERE clause")
    print("=" * 70)
    print()
    
    engine = Engine(debug=True, use_polars=True, first_match_only=False)
    
    engine.register("products", lambda: load_jsonl_file(products_file))
    engine.register("images", lambda: load_jsonl_file(images_file))
    
    row_count = 0
    checked_values = set()
    
    try:
        for row in engine.query(query):
            row_count += 1
            checked = row.get("checked")
            checked_values.add(checked)
            
            if row_count <= 5:
                print(f"Row {row_count}: product_id={row.get('product_id')}, checked={checked}")
            
            if row_count >= 20:
                break
        
        print()
        print(f"Total rows returned: {row_count}")
        print(f"Checked values found: {checked_values}")
        print()
        
        if checked_values == {1} and row_count <= 20:
            print("✅ WHERE clause working correctly!")
        else:
            print(f"❌ WHERE clause NOT working - found {checked_values}, expected only {{1}}")
            print(f"   Row count: {row_count} (should be limited by WHERE)")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
