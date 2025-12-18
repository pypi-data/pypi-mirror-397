"""
Test what required_columns are calculated for the query.
"""

from streaming_sql_engine.parser import parse_sql
from streaming_sql_engine.planner import build_logical_plan
from streaming_sql_engine.optimizer import analyze_required_columns

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

print("Analyzing required columns...")
ast = parse_sql(query)
plan = build_logical_plan(ast, {"products", "images"})

print(f"\nRequired columns:")
for table, cols in plan.required_columns.items():
    print(f"  {table}: {sorted(cols)}")

print(f"\nExpected for images table:")
print(f"  Should include: image, image_type, product_id (for join)")







