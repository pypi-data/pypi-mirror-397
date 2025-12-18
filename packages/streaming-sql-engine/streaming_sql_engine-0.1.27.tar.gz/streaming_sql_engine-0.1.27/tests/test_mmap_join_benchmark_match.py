"""Test MMAP Join matching exact benchmark configuration."""

import sys
import os
import json
from functools import partial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streaming_sql_engine import Engine

def load_jsonl_file(filename, dynamic_where=None, dynamic_columns=None):
    """Load JSONL file with optional column pruning and filter pushdown."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                
                # Apply filter pushdown if WHERE clause provided
                if dynamic_where:
                    where_lower = dynamic_where.lower().replace(" ", "")
                    if ("checked=1" in where_lower or "checked='1'" in where_lower or 
                        "checked=\"1\"" in where_lower or ".checked=1" in where_lower or
                        ".checked='1'" in where_lower or ".checked=\"1\"" in where_lower):
                        if row.get("checked") != 1:
                            continue
                
                # Apply column pruning if columns specified
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                
                yield row

def main():
    products_file = "products_3.jsonl"
    images_file = "images_3.jsonl"
    
    # Check if files exist
    if not os.path.exists(products_file):
        print(f"[ERROR] File not found: {products_file}")
        return
    
    if not os.path.exists(images_file):
        print(f"[ERROR] File not found: {images_file}")
        return
    
    # Query matching benchmark
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
    
    print("="*70)
    print("MMAP JOIN TEST - Matching Benchmark Configuration")
    print("="*70)
    print(f"\nQuery:\n{query}")
    
    # Engine config matching benchmark "4. MMAP Join"
    engine = Engine(
        debug=False,  # Set to False to avoid Unicode issues in Windows console
        use_polars=False,
        first_match_only=False
    )
    
    # Register sources matching benchmark
    engine.register(
        "products",
        partial(load_jsonl_file, products_file),
        filename=products_file
    )
    
    engine.register(
        "images",
        partial(load_jsonl_file, images_file),
        filename=images_file
    )
    
    print("\nExecuting query...")
    print("-"*70)
    
    row_count = 0
    rows_with_images = 0
    rows_without_images = 0
    products_seen = {}
    first_few_rows = []
    
    try:
        for row in engine.query(query):
            row_count += 1
            
            # Extract product_id
            pid = row.get("product_id")
            
            # Extract image
            img = row.get("image")
            
            if img:
                rows_with_images += 1
            else:
                rows_without_images += 1
            
            # Track products
            if pid not in products_seen:
                products_seen[pid] = {"total": 0, "with_images": 0, "without_images": 0}
            products_seen[pid]["total"] += 1
            if img:
                products_seen[pid]["with_images"] += 1
            else:
                products_seen[pid]["without_images"] += 1
            
            # Store first few rows
            if len(first_few_rows) < 10:
                first_few_rows.append({
                    "product_id": pid,
                    "image": img,
                    "row_keys": list(row.keys())
                })
            
            # Limit for testing
            if row_count >= 2000:
                break
    
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nResults:")
    print(f"  Total rows: {row_count:,}")
    print(f"  Rows with images: {rows_with_images:,}")
    print(f"  Rows without images: {rows_without_images:,}")
    print(f"  Unique products: {len(products_seen)}")
    
    print(f"\nFirst 10 rows:")
    for i, r in enumerate(first_few_rows, 1):
        print(f"  Row {i}: product_id={r['product_id']}, image={'HAS IMAGE' if r['image'] else 'NULL'}")
    
    print(f"\nSample products breakdown:")
    for pid in sorted(products_seen.keys())[:10]:
        info = products_seen[pid]
        status = "OK" if info["without_images"] == 0 else "ISSUE"
        print(f"  Product {pid}: {info['total']} rows ({info['with_images']} with images, {info['without_images']} without) [{status}]")
    
    # Check for issues
    issues = []
    if rows_without_images > 0:
        issues.append(f"Found {rows_without_images:,} rows with NULL images")
    
    # Check if products are getting multiple rows
    single_row_products = sum(1 for pid, info in products_seen.items() if info["total"] == 1)
    multi_row_products = len(products_seen) - single_row_products
    
    print(f"\nProducts with single row: {single_row_products}")
    print(f"Products with multiple rows: {multi_row_products}")
    
    if single_row_products == len(products_seen) and rows_without_images > 0:
        issues.append(f"All products have only 1 row with NULL images - join not finding matches!")
    
    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] Test passed!")

if __name__ == "__main__":
    main()

