"""
Test Merge Join directly without ProjectIterator to see if WHERE works.
"""

import json
from streaming_sql_engine.executor import execute_plan
from streaming_sql_engine.planner import build_logical_plan
from streaming_sql_engine.parser import parse_sql

def load_jsonl_file(filename):
    """Load JSONL file line by line."""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    products_file = "products_2.jsonl"
    images_file = "images_2.jsonl"
    
    # Parse query
    query = """
        SELECT 
            products.product_id,
            products.checked,
            products.title,
            images.image
        FROM products
        LEFT JOIN images ON products.product_id = images.product_id
        WHERE products.checked = 1
    """
    
    print("=" * 70)
    print("TESTING MERGE JOIN DIRECTLY")
    print("=" * 70)
    print()
    print("Query:")
    print(query)
    print()
    
    # Parse SQL
    ast = parse_sql(query)
    registered_tables = {"products", "images"}
    plan = build_logical_plan(ast, registered_tables)
    
    # Setup sources
    sources = {
        "products": lambda: load_jsonl_file(products_file),
        "images": lambda: load_jsonl_file(images_file)
    }
    
    source_metadata = {
        "products": {"ordered_by": "product_id"},
        "images": {"ordered_by": "product_id"}
    }
    
    print("Executing plan with debug=True...")
    print()
    
    # Execute with debug
    iterator = execute_plan(
        plan,
        sources,
        source_metadata,
        debug=True,
        use_polars=False
    )
    
    print()
    print("Results:")
    print()
    
    results = []
    try:
        for i, row in enumerate(iterator):
            results.append(row)
            if i < 5:  # Show first 5
                print(f"  Row {i+1}: {row}")
            if i >= 100:  # Limit to avoid too much output
                print(f"  ... (showing first 100 rows)")
                break
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print(f"Total rows processed: {len(results)}")
    
    if len(results) > 0:
        print()
        print("Sample results:")
        for i, row in enumerate(results[:5]):
            print(f"  {i+1}. product_id={row.get('product_id')}, checked={row.get('checked')}, image={row.get('image')}")
    else:
        print()
        print("[WARNING] No results!")
        print("This suggests:")
        print("  1. WHERE clause is filtering out all rows")
        print("  2. OR Merge Join is not producing any rows")
        print("  3. OR there's an issue with the join logic")


if __name__ == "__main__":
    main()










