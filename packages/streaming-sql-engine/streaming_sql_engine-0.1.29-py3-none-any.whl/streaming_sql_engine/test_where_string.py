"""
Test lookup join with WHERE clause using string comparison.
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
    
    # Count products with title containing "Product 1"
    products_with_title_1 = []
    for line in open(products_file):
        if line.strip():
            product = json.loads(line)
            if "Product 1" in product.get("title", ""):
                products_with_title_1.append(product)
    
    print("=" * 70)
    print("Testing WHERE clause with STRING comparison")
    print("=" * 70)
    print()
    print(f"Products with title containing 'Product 1': {len(products_with_title_1)}")
    print()
    
    # Query with WHERE clause using string comparison
    query = """
        SELECT 
            products.product_id,
            products.title,
            products.checked,
            images.image
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
        WHERE products.title = 'Product 1'
    """
    
    print(f"Query:")
    print(query)
    print()
    
    engine = Engine(debug=True, use_polars=False, first_match_only=False)
    
    engine.register("products", lambda: load_jsonl_file(products_file))
    engine.register("images", lambda: load_jsonl_file(images_file))
    
    print("Executing query...")
    print("-" * 70)
    
    results = []
    titles_found = set()
    row_count = 0
    
    try:
        for row in engine.query(query):
            row_count += 1
            title = row.get("title")
            titles_found.add(title)
            
            if row_count <= 10:
                print(f"Row {row_count}: product_id={row.get('product_id')}, title={title}, checked={row.get('checked')}")
                print(f"  All keys in row: {list(row.keys())}")
            
            if row_count >= 20:
                break
        
        print()
        print(f"Total rows returned: {row_count}")
        print(f"Titles found: {titles_found}")
        print()
        
        if len(titles_found) == 1 and "Product 1" in titles_found:
            print("✅ WHERE clause working correctly with string comparison!")
        else:
            print(f"❌ WHERE clause NOT working - found titles {titles_found}, expected only {{'Product 1'}}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
