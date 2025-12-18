"""
Comprehensive benchmark comparing all engine configurations with 1K test data.
"""

import json
import time
import psutil
import os
from functools import partial
from streaming_sql_engine import Engine


def load_jsonl_file(filename, dynamic_where=None, dynamic_columns=None):
    """
    Load JSONL file with optional column pruning and filter pushdown.
    
    Args:
        dynamic_where: SQL WHERE clause string (for filter pushdown)
        dynamic_columns: List of column names to read (for column pruning)
    """
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                
                # Apply filter pushdown if WHERE clause provided
                if dynamic_where:
                    # Handle table-prefixed and non-prefixed, quoted and unquoted values
                    # Examples: "products.checked = 1", "checked = '1'", "checked=1", etc.
                    # Normalize the WHERE clause for easier matching
                    where_lower = dynamic_where.lower().replace(" ", "")
                    
                    # Check for checked=1 patterns (with various formats)
                    if ("checked=1" in where_lower or "checked='1'" in where_lower or 
                        "checked=\"1\"" in where_lower or ".checked=1" in where_lower or
                        ".checked='1'" in where_lower or ".checked=\"1\"" in where_lower):
                        if row.get("checked") != 1:
                            continue
                    # Check for checked=0 patterns
                    elif ("checked=0" in where_lower or "checked='0'" in where_lower or
                          "checked=\"0\"" in where_lower or ".checked=0" in where_lower or
                          ".checked='0'" in where_lower or ".checked=\"0\"" in where_lower):
                        if row.get("checked") != 0:
                            continue
                
                # Apply column pruning if columns specified
                if dynamic_columns:
                    pruned_row = {k: v for k, v in row.items() if k in dynamic_columns}
                    yield pruned_row
                else:
                    yield row


def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # Convert to MB


def get_cpu_percent():
    """Get current CPU usage percentage."""
    return psutil.cpu_percent(interval=0.1)


def analyze_results(output_file, expected_products_checked_1):
    """Analyze results for inconsistencies."""
    issues = []
    
    if not os.path.exists(output_file):
        return [f"Output file not found: {output_file}"]
    
    rows = []
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    
    total_rows = len(rows)
    
    # Check row count consistency
    if total_rows == 0:
        issues.append(f"  ❌ No rows returned")
    
    # Check for missing images (should have images for products with checked=1)
    products_with_images = set()
    products_without_images = set()
    
    for row in rows:
        product_id = row.get("product_id")
        image = row.get("image")
        
        if image is None:
            products_without_images.add(product_id)
        else:
            products_with_images.add(product_id)
    
    # Check if we're getting products with checked=0 (shouldn't happen with WHERE filter)
    # Note: checked column might not be in SELECT, so we can't check this directly
    
    # Check for duplicate product_ids (should have multiple rows per product if multiple images)
    product_counts = {}
    for row in rows:
        pid = row.get("product_id")
        product_counts[pid] = product_counts.get(pid, 0) + 1
    
    # Expected: Each product with checked=1 should have at least 1 row (with or without images)
    # But we expect most to have images
    
    return {
        "total_rows": total_rows,
        "unique_products": len(product_counts),
        "products_with_images": len(products_with_images),
        "products_without_images": len(products_without_images),
        "issues": issues
    }


def run_benchmark(name, engine_config, source_config, query, products_file, images_file, expected_products_checked_1):
    """
    Run a benchmark with specific configuration.
    
    Returns:
        dict with results: rows, time_seconds, peak_memory_mb, avg_cpu_percent
    """
    print(f"\n{'='*70}")
    print(f"CONFIGURATION: {name}")
    print(f"{'='*70}")
    
    # Initialize engine
    engine = Engine(**engine_config)
    
    # Register sources
    products_source_fn = source_config.get("products_fn", partial(load_jsonl_file, products_file))
    images_source_fn = source_config.get("images_fn", partial(load_jsonl_file, images_file))
    
    engine.register(
        "products",
        products_source_fn,
        **source_config.get("products_metadata", {})
    )
    
    engine.register(
        "images",
        images_source_fn,
        **source_config.get("images_metadata", {})
    )
    
    # Measure baseline memory
    baseline_memory = get_memory_usage()
    
    # Start CPU monitoring
    cpu_samples = []
    
    # Execute query and measure
    start_time = time.time()
    peak_memory = baseline_memory
    row_count = 0
    
    # Prepare output file name
    safe_name = name.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "").replace("+", "_")
    output_file = f"results_1k_{safe_name}.jsonl"
    output_rows = []
    
    try:
        for row in engine.query(query):
            row_count += 1
            output_rows.append(row)  # Store for export
            
            # Monitor memory
            current_memory = get_memory_usage()
            if current_memory > peak_memory:
                peak_memory = current_memory
            
            # Sample CPU every 100 rows
            if row_count % 100 == 0:
                cpu_samples.append(get_cpu_percent())
        
        elapsed_time = time.time() - start_time
        
        # Calculate average CPU
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        
        # Memory overhead
        memory_overhead = peak_memory - baseline_memory
        
        # Export results to JSONL file
        with open(output_file, "w", encoding="utf-8") as f:
            for row in output_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        
        # Analyze results
        analysis = analyze_results(output_file, expected_products_checked_1)
        
        results = {
            "name": name,
            "rows": row_count,
            "time_seconds": elapsed_time,
            "peak_memory_mb": peak_memory,
            "baseline_memory_mb": baseline_memory,
            "memory_overhead_mb": memory_overhead,
            "avg_cpu_percent": avg_cpu,
            "rows_per_second": row_count / elapsed_time if elapsed_time > 0 else 0,
            "output_file": output_file,
            "output_file_size_mb": file_size_mb,
            "analysis": analysis
        }
        
        print(f"  Results:")
        print(f"    Rows processed: {row_count:,}")
        print(f"    Unique products: {analysis['unique_products']}")
        print(f"    Products with images: {analysis['products_with_images']}")
        print(f"    Products without images: {analysis['products_without_images']}")
        print(f"    Time: {elapsed_time:.2f} seconds")
        print(f"    Speed: {results['rows_per_second']:,.0f} rows/second")
        print(f"    Peak memory: {peak_memory:.2f} MB")
        print(f"    Memory overhead: {memory_overhead:.2f} MB")
        print(f"    Avg CPU: {avg_cpu:.1f}%")
        print(f"    Exported to: {output_file} ({file_size_mb:.2f} MB)")
        
        if analysis['issues']:
            print(f"    ⚠️  Issues found:")
            for issue in analysis['issues']:
                print(f"      {issue}")
        
        return results
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": name,
            "error": str(e),
            "rows": 0,
            "time_seconds": 0,
            "peak_memory_mb": 0,
            "memory_overhead_mb": 0,
            "avg_cpu_percent": 0,
            "rows_per_second": 0,
            "output_file": None,
            "output_file_size_mb": 0,
            "analysis": {"issues": [f"Error: {str(e)}"]}
        }


def main():
    products_file = "products_3.jsonl"
    images_file = "images_3.jsonl"
    
    # Check if files exist
    if not os.path.exists(products_file):
        print(f"[ERROR] File not found: {products_file}")
        print("Run: python generate_test_data_1k.py")
        return
    
    if not os.path.exists(images_file):
        print(f"[ERROR] File not found: {images_file}")
        print("Run: python generate_test_data_1k.py")
        return
    
    # Calculate expected values
    products_checked_1 = sum(1 for line in open(products_file) if line.strip() and json.loads(line).get("checked") == 1)
    
    # Build images index
    images_by_product = {}
    for line in open(images_file):
        if line.strip():
            img = json.loads(line)
            pid = img.get("product_id")
            if pid not in images_by_product:
                images_by_product[pid] = []
            images_by_product[pid].append(img)
    
    expected_rows = sum(len(images_by_product.get(json.loads(line).get("product_id"), [])) 
                       for line in open(products_file) 
                       if line.strip() and json.loads(line).get("checked") == 1)
    
    # Query to test
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
    
    print("=" * 70)
    print("COMPREHENSIVE BENCHMARK: All Engine Configurations (1K Test)")
    print("=" * 70)
    print()
    print(f"Data files:")
    print(f"  Products: {products_file}")
    print(f"  Images: {images_file}")
    print()
    print(f"Expected:")
    print(f"  Products with checked=1: {products_checked_1}")
    print(f"  Expected joined rows: ~{expected_rows}")
    print()
    print(f"Query:")
    print(query)
    print()
    
    # Define all configurations to test
    configurations = [
        {
            "name": "1. Merge Join (Sorted Data)",
            "engine_config": {
                "debug": False,
                "use_polars": False,
                "first_match_only": False
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {"ordered_by": "product_id"},
                "images_metadata": {"ordered_by": "product_id"}
            }
        },
        {
            "name": "2. Lookup Join (Default Python)",
            "engine_config": {
                "debug": False,
                "use_polars": False,
                "first_match_only": False
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {},
                "images_metadata": {}
            }
        },
        {
            "name": "3. Polars Join",
            "engine_config": {
                "debug": False,
                "use_polars": True,
                "first_match_only": False
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {},
                "images_metadata": {}
            }
        },
        {
            "name": "4. MMAP Join",
            "engine_config": {
                "debug": False,
                "use_polars": False,
                "first_match_only": False
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {"filename": products_file},
                "images_metadata": {"filename": images_file}
            }
        },
        {
            "name": "5. Polars + Column Pruning",
            "engine_config": {
                "debug": False,
                "use_polars": True,
                "first_match_only": False
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {},
                "images_metadata": {}
            }
        },
        {
            "name": "6. Polars + Filter Pushdown",
            "engine_config": {
                "debug": False,
                "use_polars": True,
                "first_match_only": False
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {},
                "images_metadata": {}
            }
        },
        {
            "name": "7. All Optimizations Combined",
            "engine_config": {
                "debug": False,
                "use_polars": True,
                "first_match_only": True
            },
            "source_config": {
                "products_fn": partial(load_jsonl_file, products_file),
                "images_fn": partial(load_jsonl_file, images_file),
                "products_metadata": {},
                "images_metadata": {}
            }
        },
    ]
    
    # Run all benchmarks
    all_results = []
    for config in configurations:
        result = run_benchmark(
            config["name"],
            config["engine_config"],
            config["source_config"],
            query,
            products_file,
            images_file,
            products_checked_1
        )
        all_results.append(result)
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Print summary
    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Configuration':<40} {'Rows':>12} {'Unique':>8} {'With Img':>10} {'Time (s)':>10} {'Memory (MB)':>12}")
    print("-" * 100)
    
    for result in all_results:
        if "error" in result:
            print(f"{result['name']:<40} {'ERROR':>12}")
        else:
            analysis = result.get('analysis', {})
            print(f"{result['name']:<40} {result['rows']:>12,} {analysis.get('unique_products', 0):>8} "
                  f"{analysis.get('products_with_images', 0):>10} {result['time_seconds']:>10.2f} "
                  f"{result['memory_overhead_mb']:>12.2f}")
    
    print()
    print("=" * 70)
    print("CONSISTENCY CHECK")
    print("=" * 70)
    print()
    
    # Check for inconsistencies
    valid_results = [r for r in all_results if "error" not in r]
    if valid_results:
        # Get row counts
        row_counts = [r['rows'] for r in valid_results]
        unique_counts = [r.get('analysis', {}).get('unique_products', 0) for r in valid_results]
        
        # Check if all configurations return similar row counts
        min_rows = min(row_counts)
        max_rows = max(row_counts)
        
        print(f"Row count range: {min_rows:,} - {max_rows:,}")
        print(f"Expected: ~{expected_rows}")
        
        if max_rows - min_rows > expected_rows * 0.1:  # More than 10% difference
            print(f"  WARNING: Large variation in row counts ({max_rows - min_rows} rows difference)")
            print(f"     This indicates inconsistencies between join algorithms")
        
        # Check which configurations are inconsistent
        print()
        print("Configuration comparison:")
        for result in valid_results:
            analysis = result.get('analysis', {})
            status = "OK" if abs(result['rows'] - expected_rows) < expected_rows * 0.1 else "ISSUE"
            print(f"  {status} {result['name']}: {result['rows']:,} rows "
                  f"(unique: {analysis.get('unique_products', 0)}, "
                  f"with images: {analysis.get('products_with_images', 0)})")


if __name__ == "__main__":
    main()







