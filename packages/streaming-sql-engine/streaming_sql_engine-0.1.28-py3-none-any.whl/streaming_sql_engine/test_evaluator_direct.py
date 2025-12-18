"""Direct test of evaluator with integer comparison."""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlglot import parse_one
from streaming_sql_engine.evaluator import evaluate_expression

# Test 1: Integer comparison
print("Test 1: Integer comparison")
expr1 = parse_one("SELECT * FROM t WHERE checked = 1").args['where'].this
print(f"Expression: {expr1}")
print(f"Expression type: {type(expr1)}")
print(f"Left: {expr1.this} (type={type(expr1.this)})")
print(f"Right: {expr1.expression} (type={type(expr1.expression)})")
if hasattr(expr1.expression, 'this'):
    print(f"  Right.this: {expr1.expression.this} (type={type(expr1.expression.this)})")

row1 = {"checked": 1}
print(f"Row: {row1}")
print(f"Evaluating left side...")
left_val = evaluate_expression(expr1.this, row1)
print(f"  Left value: {left_val} (type={type(left_val)})")
print(f"Evaluating right side...")
right_val = evaluate_expression(expr1.expression, row1)
print(f"  Right value: {right_val} (type={type(right_val)})")
print(f"Comparing: {left_val} == {right_val} -> {left_val == right_val}")
result1 = evaluate_expression(expr1, row1)
print(f"Result: {result1} (type={type(result1)})")
print()

# Test 2: String comparison  
print("Test 2: String comparison")
expr2 = parse_one("SELECT * FROM t WHERE title = 'Product 1'").args['where'].this
print(f"Expression: {expr2}")
print(f"Left: {expr2.this}, Right: {expr2.expression}")

row2 = {"title": "Product 1"}
print(f"Row: {row2}")
result2 = evaluate_expression(expr2, row2)
print(f"Result: {result2} (type={type(result2)})")
print()

# Test 3: Prefixed column name
print("Test 3: Prefixed column name with integer")
expr3 = parse_one("SELECT * FROM t WHERE products.checked = 1").args['where'].this
print(f"Expression: {expr3}")
print(f"Left: {expr3.this} (table={expr3.this.table}, name={expr3.this.name})")
print(f"Right: {expr3.expression} (value={expr3.expression.this})")

row3 = {"products.checked": 1, "checked": 0}
print(f"Row: {row3}")
result3 = evaluate_expression(expr3, row3)
print(f"Result: {result3} (type={type(result3)})")
print()

# Test 4: Prefixed column name with wrong value
print("Test 4: Prefixed column name with wrong value")
row4 = {"products.checked": 0, "checked": 1}
print(f"Row: {row4}")
result4 = evaluate_expression(expr3, row4)
print(f"Result: {result4} (type={type(result4)})")
