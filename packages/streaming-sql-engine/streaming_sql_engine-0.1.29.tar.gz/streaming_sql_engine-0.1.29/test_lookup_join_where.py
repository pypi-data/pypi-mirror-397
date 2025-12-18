"""
Test lookup join with WHERE clause to verify correctness.
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
    
    # Check if files exist
    if not os.path.exists(products_file):
        print(f"[ERROR] File not found: {products_file}")
        return
    
    if not os.path.exists(images_file):
        print(f"[ERROR] File not found: {images_file}")
        return
    
    # Count expected values
    products_checked_1 = []
    products_all = []
    for line in open(products_file):
        if line.strip():
            product = json.loads(line)
            products_all.append(product)
            if product.get("checked") == 1:
                products_checked_1.append(product)
    
    # Build images index
    images_by_product = {}
    for line in open(images_file):
        if line.strip():
            img = json.loads(line)
            pid = img.get("product_id")
            if pid not in images_by_product:
                images_by_product[pid] = []
            images_by_product[pid].append(img)
    
    # Calculate expected joined rows
    # For LEFT JOIN: each product with checked=1 should produce rows equal to number of images
    # If no images, still 1 row (with NULL image)
    expected_rows = 0
    expected_products = set()
    for product in products_checked_1:
        pid = product.get("product_id")
        expected_products.add(pid)
        image_count = len(images_by_product.get(pid, []))
        expected_rows += max(1, image_count) if image_count > 0 else 1
    
    print("=" * 70)
    print("TEST: Lookup Join with WHERE Clause")
    print("=" * 70)
    print()
    print(f"Data files:")
    print(f"  Products: {products_file} ({len(products_all)} total)")
    print(f"  Images: {images_file}")
    print()
    print(f"Expected:")
    print(f"  Products with checked=1: {len(products_checked_1)}")
    print(f"  Expected joined rows: {expected_rows}")
    print(f"  Expected unique products in result: {len(expected_products)}")
    print()
    
    # Query with WHERE clause
    query = """
        SELECT 
            products.product_id,
            products.product_sku,
            products.title,
            products.checked,
            images.image,
            images.image_type
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
        WHERE products.checked = 1
    """
    
    print(f"Query:")
    print(query)
    print()
    
    # Initialize engine with LOOKUP JOIN (not merge, not polars, not mmap)
    engine = Engine(
        debug=True,  # Enable debug to see WHERE clause handling
        use_polars=False,  # Force Python lookup join
        first_match_only=False
    )
    
    # Register sources WITHOUT ordered_by or filename (forces lookup join)
    engine.register(
        "products",
        lambda: load_jsonl_file(products_file),
        # No ordered_by = lookup join
        # No filename = not mmap
    )
    
    engine.register(
        "images",
        lambda: load_jsonl_file(images_file),
        # No ordered_by = lookup join
        # No filename = not mmap
    )
    
    # Execute query
    print("Executing query...")
    print("-" * 70)
    
    results = []
    product_ids_seen = set()
    products_with_images = set()
    products_without_images = set()
    checked_values = set()
    
    try:
        for row in engine.query(query):
            results.append(row)
            pid = row.get("product_id")
            product_ids_seen.add(pid)
            checked = row.get("checked")
            checked_values.add(checked)
            
            if row.get("image") is not None:
                products_with_images.add(pid)
            else:
                products_without_images.add(pid)
        
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print()
        print(f"Total rows returned: {len(results)}")
        print(f"Expected rows: {expected_rows}")
        print(f"Difference: {len(results) - expected_rows}")
        print()
        print(f"Unique products in result: {len(product_ids_seen)}")
        print(f"Expected unique products: {len(expected_products)}")
        print()
        print(f"Products with images: {len(products_with_images)}")
        print(f"Products without images: {len(products_without_images)}")
        print()
        print(f"Checked values in result: {checked_values}")
        print()
        
        # Validation
        issues = []
        
        # Check 1: All rows should have checked=1
        if checked_values != {1}:
            issues.append(f"❌ FAIL: Found checked values {checked_values}, expected only {{1}}")
        else:
            print("✅ PASS: All rows have checked=1")
        
        # Check 2: Row count should match expected
        if abs(len(results) - expected_rows) > 5:  # Allow small tolerance
            issues.append(f"❌ FAIL: Row count {len(results)} doesn't match expected {expected_rows} (diff: {abs(len(results) - expected_rows)})")
        else:
            print(f"✅ PASS: Row count matches expected ({len(results)} vs {expected_rows})")
        
        # Check 3: All expected products should be present
        missing_products = expected_products - product_ids_seen
        if missing_products:
            issues.append(f"❌ FAIL: Missing products: {list(missing_products)[:10]}")
        else:
            print(f"✅ PASS: All expected products present ({len(product_ids_seen)})")
        
        # Check 4: No unexpected products
        unexpected_products = product_ids_seen - expected_products
        if unexpected_products:
            issues.append(f"❌ FAIL: Unexpected products: {list(unexpected_products)[:10]}")
        else:
            print(f"✅ PASS: No unexpected products")
        
        # Check 5: Sample first few rows
        print()
        print("Sample rows (first 5):")
        for i, row in enumerate(results[:5]):
            print(f"  Row {i+1}: product_id={row.get('product_id')}, checked={row.get('checked')}, "
                  f"has_image={row.get('image') is not None}")
        
        print()
        print("=" * 70)
        if issues:
            print("VALIDATION FAILED")
            print("=" * 70)
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("VALIDATION PASSED ✅")
            print("=" * 70)
            print()
            print("All checks passed! The lookup join with WHERE clause is working correctly.")
            return True
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
