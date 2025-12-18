"""
Comprehensive benchmark comparing all engine configurations with RAM and CPU measurements.

Tests:
1. Merge Join (sorted data, use_polars=False, ordered_by)
2. Lookup Join (default Python join)
3. Polars Join (use_polars=True)
4. MMAP Join (filename metadata, use_polars=False)
5. Polars + Column Pruning (use_polars=True, dynamic_columns protocol)
6. Polars + Filter Pushdown (use_polars=True, dynamic_where protocol)
7. All Optimizations Combined (Polars + Column Pruning + Filter Pushdown + first_match_only)
"""

import json
import time
import psutil
import os
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


def run_benchmark(name, engine_config, source_config, query, products_file, images_file):
    """
    Run a benchmark with specific configuration.
    
    Returns:
        dict with results: rows, time_seconds, peak_memory_mb, avg_cpu_percent
    """
    print(f"\n{'='*70}")
    print(f"CONFIGURATION: {name}")
    print(f"{'='*70}")
    print(f"Engine config: {engine_config}")
    print(f"Source config: {source_config}")
    print()
    
    # Initialize engine
    engine = Engine(**engine_config)
    
    # Register sources
    products_source_fn = source_config.get("products_fn", lambda: load_jsonl_file(products_file))
    images_source_fn = source_config.get("images_fn", lambda: load_jsonl_file(images_file))
    
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
    output_file = f"results_{safe_name}.jsonl"
    output_rows = []
    
    try:
        for row in engine.query(query):
            row_count += 1
            output_rows.append(row)  # Store for export
            
            # Monitor memory
            current_memory = get_memory_usage()
            if current_memory > peak_memory:
                peak_memory = current_memory
            
            # Sample CPU every 1000 rows
            if row_count % 1000 == 0:
                cpu_samples.append(get_cpu_percent())
            
            # Limit output for very large result sets
            if row_count >= 1000000:  # Cap at 1M rows for testing
                print(f"  [INFO] Capped at 1M rows for performance testing")
                break
        
        elapsed_time = time.time() - start_time
        
        # Calculate average CPU
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        
        # Memory overhead
        memory_overhead = peak_memory - baseline_memory
        
        # Export results to JSONL file
        export_start = time.time()
        with open(output_file, "w", encoding="utf-8") as f:
            for row in output_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        export_time = time.time() - export_start
        
        import os
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        
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
            "output_file_size_mb": file_size_mb
        }
        
        print(f"  Results:")
        print(f"    Rows processed: {row_count:,}")
        print(f"    Time: {elapsed_time:.2f} seconds")
        print(f"    Speed: {results['rows_per_second']:,.0f} rows/second")
        print(f"    Peak memory: {peak_memory:.2f} MB")
        print(f"    Memory overhead: {memory_overhead:.2f} MB")
        print(f"    Avg CPU: {avg_cpu:.1f}%")
        print(f"    Exported to: {output_file} ({file_size_mb:.2f} MB)")
        
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
            "output_file_size_mb": 0
        }


def main():
    products_file = "products_3_1k.jsonl"
    images_file = "images_3_1k.jsonl"
    
    # Check if files exist
    if not os.path.exists(products_file):
        print(f"[ERROR] File not found: {products_file}")
        print("Run: python generate_test_data_100k.py")
        return
    
    if not os.path.exists(images_file):
        print(f"[ERROR] File not found: {images_file}")
        print("Run: python generate_test_data_100k.py")
        return
    
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
    print("COMPREHENSIVE BENCHMARK: All Engine Configurations")
    print("=" * 70)
    print()
    print(f"Data files:")
    print(f"  Products: {products_file}")
    print(f"  Images: {images_file}")
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
                "products_fn": lambda: load_jsonl_file(products_file),
                "images_fn": lambda: load_jsonl_file(images_file),
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
                "products_fn": lambda: load_jsonl_file(products_file),
                "images_fn": lambda: load_jsonl_file(images_file),
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
                "products_fn": lambda: load_jsonl_file(products_file),
                "images_fn": lambda: load_jsonl_file(images_file),
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
                "products_fn": lambda: load_jsonl_file(products_file),
                "images_fn": lambda: load_jsonl_file(images_file),
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
                "products_fn": lambda dynamic_where=None, dynamic_columns=None: load_jsonl_file(
                    products_file, dynamic_where=dynamic_where, dynamic_columns=dynamic_columns
                ),
                "images_fn": lambda dynamic_where=None, dynamic_columns=None: load_jsonl_file(
                    images_file, dynamic_where=dynamic_where, dynamic_columns=dynamic_columns
                ),
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
                "products_fn": lambda dynamic_where=None, dynamic_columns=None: load_jsonl_file(
                    products_file, dynamic_where=dynamic_where, dynamic_columns=dynamic_columns
                ),
                "images_fn": lambda dynamic_where=None, dynamic_columns=None: load_jsonl_file(
                    images_file, dynamic_where=dynamic_where, dynamic_columns=dynamic_columns
                ),
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
                "products_fn": lambda dynamic_where=None, dynamic_columns=None: load_jsonl_file(
                    products_file, dynamic_where=dynamic_where, dynamic_columns=dynamic_columns
                ),
                "images_fn": lambda dynamic_where=None, dynamic_columns=None: load_jsonl_file(
                    images_file, dynamic_where=dynamic_where, dynamic_columns=dynamic_columns
                ),
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
            images_file
        )
        all_results.append(result)
        
        # Small delay between tests
        time.sleep(1)
    
    # Print summary
    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Configuration':<40} {'Rows':>12} {'Time (s)':>10} {'Memory (MB)':>12} {'CPU %':>8} {'Rows/s':>12} {'Output File':<30}")
    print("-" * 130)
    
    for result in all_results:
        if "error" in result:
            print(f"{result['name']:<40} {'ERROR':>12} {'':>30}")
        else:
            output_info = f"{result.get('output_file', 'N/A')} ({result.get('output_file_size_mb', 0):.2f} MB)" if result.get('output_file') else "N/A"
            print(f"{result['name']:<40} {result['rows']:>12,} {result['time_seconds']:>10.2f} "
                  f"{result['memory_overhead_mb']:>12.2f} {result['avg_cpu_percent']:>8.1f} "
                  f"{result['rows_per_second']:>12,.0f} {output_info:<30}")
    
    print()
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    # Find best configuration for each metric
    valid_results = [r for r in all_results if "error" not in r]
    
    if valid_results:
        fastest = min(valid_results, key=lambda x: x["time_seconds"])
        lowest_memory = min(valid_results, key=lambda x: x["memory_overhead_mb"])
        highest_throughput = max(valid_results, key=lambda x: x["rows_per_second"])
        
        print(f"Fastest: {fastest['name']} ({fastest['time_seconds']:.2f}s)")
        print(f"Lowest Memory: {lowest_memory['name']} ({lowest_memory['memory_overhead_mb']:.2f} MB)")
        print(f"Highest Throughput: {highest_throughput['name']} ({highest_throughput['rows_per_second']:,.0f} rows/s)")
        print()
        print("For 100K+ records:")
        print("  - Use Merge Join if data is sorted (fastest + lowest memory)")
        print("  - Use MMAP Join if data is not sorted (low memory)")
        print("  - Use Polars + optimizations for best throughput")


if __name__ == "__main__":
    main()
