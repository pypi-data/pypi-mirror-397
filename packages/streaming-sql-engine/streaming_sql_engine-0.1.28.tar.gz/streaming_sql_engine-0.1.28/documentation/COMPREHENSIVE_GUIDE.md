# Join Data from Anywhere: The Streaming SQL Engine That Bridges Databases, APIs, and Files

---

Have you ever needed to join data from a MySQL database with a PostgreSQL database, a MongoDB collection, and a REST API all in one query? Traditional databases can't do this. That's why I built the Streaming SQL Engine.

---

## The Problem: Data Lives Everywhere

Modern applications don't store all their data in one place. You might have:

- User data in PostgreSQL
- Order data in MySQL
- Product catalog in MongoDB
- Pricing information from a REST API
- Inventory data in CSV files
- Product feeds in XML files

**The challenge:** How do you join all this data together?

Traditional solutions require:

- Exporting data from each system
- Importing into a central database
- Writing complex ETL pipelines
- Maintaining data synchronization

**There had to be a better way.**

---

## The Solution: Streaming SQL Engine

I built a lightweight Python library that lets you join data from **any source** using standard SQL syntax without exporting, importing, or setting up infrastructure.

## Example:

```python
from streaming_sql_engine import Engine
import psycopg2
import pymysql
from pymongo import MongoClient
import requests
import csv

engine = Engine()

# Register PostgreSQL source (iterator function)
def postgres_users():
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "email": row[2]}
    conn.close()
engine.register("postgres_users", postgres_users)

# Register MySQL source (iterator function)
def mysql_products():
    conn = pymysql.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "price": row[2]}
    conn.close()
engine.register("mysql_products", mysql_products)

# Register MongoDB source (iterator function)
def mongo_inventory():
    client = MongoClient("mongodb://localhost:27017")
    for doc in client.mydb.inventory.find():
        yield doc
engine.register("mongo_inventory", mongo_inventory)

# Register REST API source (iterator function)
def api_prices():
    response = requests.get("https://api.example.com/prices")
    for item in response.json():
        yield item
engine.register("api_prices", api_prices)

# Register CSV source (iterator function)
def csv_suppliers():
    with open("suppliers.csv") as f:
        for row in csv.DictReader(f):
            yield row
engine.register("csv_suppliers", csv_suppliers)

# Join them all in one SQL query!
query = """
    SELECT
        mysql_products.name,
        postgres_users.email,
        mongo_inventory.quantity,
        api_prices.price,
        csv_suppliers.supplier_name
    FROM mysql_products
    JOIN postgres_users ON mysql_products.user_id = postgres_users.id
    JOIN mongo_inventory ON mysql_products.sku = mongo_inventory.sku
    JOIN api_prices ON mysql_products.sku = api_prices.sku
    JOIN csv_suppliers ON mysql_products.supplier_id = csv_suppliers.id
    WHERE api_prices.price > 100
"""

for row in engine.query(query):
    process(row)
```

**That's it.** No clusters, no infrastructure, no data export - just pure Python and SQL.

---

## Why I Built This: The Problem That Needed Solving

I was working on a data reconciliation project where I needed to join data from multiple sources:

- MySQL database (product catalog)
- PostgreSQL database (user data)
- MongoDB collection (inventory)
- REST API (pricing information)
- CSV files (supplier data)

**The challenge:** Traditional databases can't join across different systems. I had three options:

1. **Export everything to one database** - Time-consuming, requires ETL pipelines, data becomes stale
2. **Write custom Python code** - Complex, error-prone, hard to maintain
3. **Use existing tools** - Spark/Flink require clusters, DuckDB requires data import, Presto needs infrastructure

**None of these worked for my use case.** I needed something that:

- Could join data from different systems without export
- Was simple to use (SQL syntax)
- Required zero infrastructure
- Worked with Python natively
- Processed data efficiently (streaming)

So I built the Streaming SQL Engine.

---

## How I Built It: Architecture and Design Decisions

### Core Design Philosophy

The engine follows a **pipeline architecture** inspired by database query execution engines (like PostgreSQL and SQLite), but implemented in pure Python using iterators.

**Key insight:** Python's iterator protocol is perfect for streaming data. Each operator in the pipeline is an iterator that processes rows one at a time.

### Why Iterator-Based Architecture?

**Key advantages:**

1. **Memory efficiency:** Only one row in memory at a time (except for join indexes)
2. **Lazy evaluation:** Processing starts only when you iterate over results
3. **Composability:** Operators can be chained arbitrarily
4. **Extensibility:** Easy to add new operators
5. **Python-native:** Uses standard Python iterator protocol

**Trade-offs:**

- **Performance:** Python iterators are slower than compiled code, but flexibility is worth it
- **Memory:** Join indexes require memory, but this is necessary for efficient joins
- **Complexity:** Iterator chains can be complex, but they're composable and testable

### Expression Evaluation

**How WHERE clauses are evaluated:**

The engine uses recursive AST traversal to evaluate expressions:

**Why recursive:** SQL expressions are trees. Recursive evaluation naturally handles nested expressions like `(a > 10 AND b < 20) OR c = 5`.

### Join Algorithm Selection

**How the engine chooses join algorithms:**

The engine follows this priority order when selecting a join algorithm:

1. **Check if both sides are sorted** (`ordered_by` metadata)

   - If yes, use `MergeJoinIterator` (most memory-efficient for sorted data)
   - Only used when `use_polars=False`

2. **Check if right side is a file** (`filename` metadata)

   - If yes, use `MmapLookupJoinIterator` (memory-mapped, 90-99% memory reduction)
   - Only used when `use_polars=False`

3. **Check if Polars is available** (`use_polars` flag)

   - If yes, use `PolarsLookupJoinIterator` (vectorized, SIMD-accelerated)
   - Used when `use_polars=True` is explicitly set

4. **Default fallback**
   - Use `LookupJoinIterator` (Python hash-based, most compatible)

**Logic:**

**Note:** When `use_polars=False` (default), Merge Join and MMAP Join are checked first before falling back to Python Lookup Join. When `use_polars=True` is explicitly set, the engine prioritizes Polars over MMAP and Merge Join.

### Protocol-Based Optimization

**The key innovation:** Automatic optimization detection via function signature inspection.

**How it works:**

1. Engine inspects source function signature using `inspect.signature()`
2. If function accepts `dynamic_where` or `dynamic_columns` parameters, it supports optimizations
3. Engine passes optimization parameters automatically
4. Source function applies optimizations (filter pushdown, column pruning)

**Why this approach:**

- **No flags needed:** Detection is automatic
- **Flexible:** Any Python function can be a source
- **Backward compatible:** Simple sources still work (no optimizations)
- **Extensible:** Easy to add new optimization parameters

**Example:**

```python
# Simple source (no optimizations)
def simple_source():
    return iter([{"id": 1, "name": "Alice"}])

# Optimized source (with protocol)
def optimized_source(dynamic_where=None, dynamic_columns=None):
    query = "SELECT "
    if dynamic_columns:
        query += ", ".join(dynamic_columns)
    else:
        query += "*"
    query += " FROM table"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"
    return execute_query(query)

# Both work the same way:
engine.register("users", simple_source)  # No optimizations
engine.register("products", optimized_source)  # Optimizations apply automatically!
```

### Memory Management

**Key strategies:**

1. **Streaming:** Process one row at a time, never load full tables
2. **Join indexes:** Only right side of joins is materialized (necessary for lookups)
3. **Memory-mapped files:** For large JSONL files, use OS virtual memory
4. **Column pruning:** Only extract needed columns
5. **Filter pushdown:** Filter at source, reduce data transfer

**Memory footprint:**

- **Left side of join:** O(1) - one row at a time
- **Right side of join:** O(n) - hash index in memory
- **Total:** O(n) where n = size of right side

**Why this works:** In most queries, the right side is smaller (e.g., joining large product table with small category table). The engine is designed to put smaller tables on the right side.

### Performance Optimizations

**1. Polars Vectorization**

When Polars is available, the engine uses vectorized operations:

```python
# Instead of row-by-row filtering:
for row in rows:
    if row['price'] > 100:
        yield row

# Use Polars batch filtering:
df = pl.DataFrame(rows)
filtered_df = df.filter(pl.col('price') > 100)
for row in filtered_df.iter_rows(named=True):
    yield row
```

**Why faster:** Polars uses SIMD instructions and columnar processing, 10-200x faster than row-by-row Python loops.

**2. Memory-Mapped Joins**

For large JSONL files, use OS virtual memory instead of loading into RAM:

```python
# Instead of loading entire file:
with open('large_file.jsonl') as f:
    data = [json.loads(line) for line in f]  # 10GB in memory!

# Use memory-mapped file:
import mmap
with open('large_file.jsonl', 'rb') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    # OS handles memory, can process files larger than RAM
```

**Why this works:** OS virtual memory allows accessing file data without loading it all into RAM. 90-99% memory reduction for large files.

**3. First Match Only Optimization**

For joins where only the first match matters (prevents Cartesian products).

**Why useful:** Prevents Cartesian products when right side has duplicate keys. Significantly reduces output size and processing time.

**4. Column Pruning**

Only extracts columns needed for the query, reducing I/O and memory:

```python
# Query only requests 'name' and 'price'
query = "SELECT name, price FROM products"

# Engine automatically requests only these columns from source
def source(dynamic_columns=None):
    columns = ", ".join(dynamic_columns)  # ['name', 'price']
    query = f"SELECT {columns} FROM table"
```

**5. Filter Pushdown**

Pushes WHERE conditions to data sources when possible:

```python
# Query has WHERE clause
query = "SELECT * FROM products WHERE price > 100"

# Engine automatically pushes filter to source
def source(dynamic_where=None):
    query = f"SELECT * FROM table WHERE {dynamic_where}"
```

**6. Merge Joins**

Efficient joins for pre-sorted data (O(n+m) time complexity):

```python
# Register with ordered_by to enable merge join
engine.register("users", users_source, ordered_by="id")

# Engine uses merge join algorithm
# Both sides must be sorted by join key
```

### Design Decisions and Trade-offs

**1. Why Python iterators instead of compiled code?**

**Decision:** Use Python iterators for flexibility

**Trade-off:** Slower than compiled code, but:

- Works with any Python data source
- Easy to extend and customize
- No compilation step needed
- Python-native integration

**2. Why separate logical planning from execution?**

**Decision:** Two-phase approach (plan then execute)

**Trade-off:** Extra step, but:

- Enables query optimization
- Easier to test and debug
- Can reuse planning logic
- Clear separation of concerns

**3. Why protocol-based optimization instead of flags?**

**Decision:** Automatic detection via function signature

**Trade-off:** Slightly more complex detection, but:

- No flags to remember
- Automatic optimization
- Backward compatible
- More Pythonic

**4. Why materialize right side of joins?**

**Decision:** Build hash index on right side

**Trade-off:** Memory usage, but:

- O(1) lookup time per left row
- Necessary for efficient joins
- Can use memory-mapped files for large files
- Standard database approach

**5. Why limit SQL features (no GROUP BY, aggregations)?**

**Decision:** Focus on joins and filtering

**Trade-off:** Less SQL support, but:

- Simpler implementation
- Faster execution
- Focuses on core use case (cross-system joins)
- Can add later if needed

### The Result

A lightweight Python library that:

- Joins data from any source using SQL
- Processes data row-by-row (streaming)
- Requires zero infrastructure
- Automatically optimizes when possible
- Works with any Python iterator

**The key insight:** Python's iterator protocol is perfect for streaming SQL execution. By combining SQL parsing, logical planning, and iterator-based execution, I created a tool that solves a real problem: joining data from different systems without complex infrastructure.

---

## How It Works: Streaming Architecture

The engine processes data **row-by-row**, never loading entire tables into memory:

```
SQL Query
    |
Parser -> AST
    |
Planner -> Logical Plan
    |
Executor -> Iterator Pipeline
    |
Results (Generator)
```

**Iterator Pipeline:**

```
ScanIterator -> FilterIterator -> JoinIterators -> ProjectIterator -> Results
```

Each iterator processes rows incrementally, enabling true streaming execution. This means:

- Low memory footprint
- Can process data larger than RAM
- Results yielded immediately
- No buffering required

---

## Supported Data Sources

The engine works with **any Python iterator**, making it incredibly flexible:

### Databases

All databases are accessed via Python iterator functions. The engine doesn't use connectors - it works with any Python function that returns an iterator:

- **PostgreSQL** - Create iterator function that queries PostgreSQL and yields rows
- **MySQL** - Create iterator function that queries MySQL and yields rows
- **MongoDB** - Create iterator function that queries MongoDB and yields documents

### Files

- **CSV** - Standard CSV files
- **JSONL** - JSON Lines format with memory-mapped joins
- **JSON** - Standard JSON files
- **XML** - XML parsing with ElementTree

### APIs

- **REST APIs** - Any HTTP endpoint
- **GraphQL** - Via custom functions
- **WebSockets** - Streaming data sources

### Custom Sources

- **Any Python function** that returns an iterator
- **Generators** - Perfect for streaming data
- **Custom transformations** - Apply Python logic between joins

---

## SQL Features

The engine supports standard SQL syntax:

### Supported Features

**SELECT** - Column selection, aliasing, table-qualified columns

```sql
SELECT users.name, orders.total AS order_total
FROM users
JOIN orders ON users.id = orders.user_id
```

**JOIN** - INNER JOIN and LEFT JOIN with equality conditions

```sql
SELECT *
FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id
LEFT JOIN table3 t3 ON t1.id = t3.id
```

**WHERE** - Comparisons, boolean logic, NULL checks, IN clauses

```sql
SELECT *
FROM products
WHERE price > 100
  AND status IN ('active', 'pending')
  AND description IS NOT NULL
```

**Arithmetic** - Addition, subtraction, multiplication, division, modulo

```sql
SELECT
  price - discount AS final_price,
  quantity * unit_price AS total
FROM orders
```

### Not Supported

- GROUP BY and aggregations (COUNT, SUM, AVG)
- ORDER BY
- HAVING
- Subqueries

_These limitations keep the engine focused on joins and filtering - its core strength._

---

## Real-World Examples

### Example 1: Microservices Data Integration

In a microservices architecture, data is distributed across services:

```python
from streaming_sql_engine import Engine
import psycopg2
import pymysql
import requests

engine = Engine()

# Service 1: User service (PostgreSQL) - iterator function
def users_source():
    conn = psycopg2.connect(host="user-db", port=5432, user="user", password="pass", database="users_db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "email": row[2]}
    conn.close()
engine.register("users", users_source)

# Service 2: Order service (MySQL) - iterator function
def orders_source():
    conn = pymysql.connect(host="order-db", port=3306, user="user", password="pass", database="orders_db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, total FROM orders")
    for row in cursor:
        yield {"id": row[0], "user_id": row[1], "total": row[2]}
    conn.close()
engine.register("orders", orders_source)

# Service 3: Payment service (REST API) - iterator function
def payment_source():
    response = requests.get("https://payments.service/api/transactions")
    for item in response.json():
        yield item
engine.register("payments", payment_source)

# Join across services
query = """
    SELECT users.name, orders.total, payments.status
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN payments ON orders.id = payments.order_id
"""
```

**Why this matters:** No need for a shared database or complex ETL pipelines. The engine accepts any Python function that returns an iterator, making it incredibly flexible.

### Example 2: Real-Time Price Comparison

Compare prices from multiple XML feeds and match with MongoDB:

```python
def parse_xml(filepath):
    tree = ET.parse(filepath)
    for product in tree.findall('.//product'):
        yield {
            'ean': product.find('ean').text,
            'price': float(product.find('price').text),
            'name': product.find('name').text
        }

engine.register("xml1", lambda: parse_xml("prices1.xml"))
engine.register("xml2", lambda: parse_xml("prices2.xml"))
engine.register("mongo", mongo_source)

query = """
    SELECT
        xml1.ean,
        xml1.price AS price1,
        xml2.price AS price2,
        mongo.sf_sku
    FROM xml1
    JOIN xml2 ON xml1.ean = xml2.ean
    JOIN mongo ON xml1.ean = mongo.ean
    WHERE xml1.price != xml2.price
"""
```

**Production results:** 17M + 17M XML records + 5M MongoDB records processed in 7 minutes using 400 MB RAM.

### Example 3: Python Processing Between Joins

Apply Python logic (ML models, custom functions) between joins:

```python
def enriched_source():
    """Source that processes data with Python before joining"""
    import psycopg2
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category_id FROM products")
    for row in cursor:
        product = {"id": row[0], "name": row[1], "category_id": row[2]}
        # Apply Python logic
        product['ml_score'] = ml_model.predict(product)
        product['custom_field'] = custom_function(product)
        yield product
    conn.close()

def categories_source():
    import psycopg2
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    for row in cursor:
        yield {"id": row[0], "category_name": row[1]}
    conn.close()

engine.register("enriched_products", enriched_source)
engine.register("categories", categories_source)

query = """
    SELECT p.name, p.ml_score, c.category_name
    FROM enriched_products p
    JOIN categories c ON p.category_id = c.id
"""
```

**Why this matters:** Seamless integration with Python ecosystem - use any library, apply any logic.

---

## Comparison with Alternatives

### vs DuckDB

| Feature                 | Streaming SQL Engine | DuckDB              |
| ----------------------- | -------------------- | ------------------- |
| Cross-system joins      | ✅ Direct            | ⚠️ Requires import  |
| API + Database join     | ✅ Direct            | ❌ Must export API  |
| Real-time streaming     | ✅ True streaming    | ⚠️ Buffering needed |
| Python processing       | ✅ Native            | ⚠️ Export/import    |
| GROUP BY / Aggregations | ❌ Not supported     | ✅ Full support     |
| Performance (same DB)   | ⚠️ Moderate          | ✅ Very fast        |

**Use Streaming SQL Engine when:** You need to join data from different systems that can't be imported into DuckDB.

**Use DuckDB when:** All data can be imported and you need aggregations.

### vs Pandas

| Feature                  | Streaming SQL Engine   | Pandas                   |
| ------------------------ | ---------------------- | ------------------------ |
| Cross-system joins       | ✅ Direct              | ❌ Must load all data    |
| Memory efficiency        | ✅ Streaming           | ❌ Loads all in memory   |
| SQL syntax               | ✅ Standard SQL        | ❌ DataFrame API         |
| Large datasets           | ✅ Can exceed RAM      | ❌ Limited by RAM        |
| Real-time data           | ✅ Streaming           | ❌ Batch only            |
| File formats             | ✅ Any Python iterator | ⚠️ Limited formats       |
| Performance (large data) | ✅ Streaming           | ⚠️ Slower for large data |

**Use Streaming SQL Engine when:** You need to join data from different systems, process data larger than RAM, or use SQL syntax.

**Use Pandas when:** All data fits in memory and you prefer DataFrame API.

---

## Are There Other Tools Like This?

**Short answer: Not exactly.**

While there are many tools that do **parts** of what Streaming SQL Engine does, none combine all these characteristics:

### What Makes Streaming SQL Engine Unique

1. **Zero Infrastructure + Cross-System Joins**

   - Most tools require clusters (Spark, Flink, Drill)
   - Or require specific infrastructure (ksqlDB needs Kafka)
   - Streaming SQL Engine: Just Python

2. **Any Python Iterator as Data Source**

   - Most tools require specific connectors
   - Streaming SQL Engine: Any Python function works

3. **Direct API Joins**

   - Most tools can't join REST APIs directly
   - Streaming SQL Engine: Native support

4. **Python-Native Architecture**
   - Most tools are Java/Rust with Python wrappers
   - Streaming SQL Engine: Pure Python, seamless integration

### Similar Tools (But Different)

**Apache Drill** - Similar cross-system capability, but requires cluster and Java

**ksqlDB** - Streaming SQL, but Kafka-only and requires infrastructure

**Materialize** - Streaming database, but requires database server

**DataFusion** - Fast SQL engine, but limited to Arrow/Parquet data

**Polars SQL** - Fast SQL, but requires loading data into DataFrames first

**Presto/Trino** - Cross-system SQL, but requires cluster infrastructure

**None of these** combine:

- Zero infrastructure
- Any Python iterator as source
- Direct API joins
- Pure Python implementation
- Simple deployment

**That's what makes Streaming SQL Engine unique.**

---

## Key Wins

### 1. Cross-System Joins

The **only tool** that can join MySQL + PostgreSQL + MongoDB + REST API + CSV files in a single SQL query without data export/import.

### 2. Zero Infrastructure

No clusters, no setup, just Python. Install and use immediately:

```bash
pip install streaming-sql-engine
```

### 3. Memory Efficient

Processes 39 million records with only 400 MB RAM. True streaming architecture means you can process data larger than available RAM.

### 4. Python-Native

Seamless integration with Python ecosystem. Use any Python function as a data source, apply ML models, use any library.

### 5. Real-Time Processing

Join live streaming data with static reference data. No buffering required - true streaming execution.

### 6. Automatic Optimizations

Filter pushdown, column pruning, and vectorization applied automatically. No configuration needed - the engine detects protocol support.

---

## When to Use Streaming SQL Engine

**Perfect for:**

- Joining data from different systems (databases, APIs, files)
- Microservices data aggregation
- Real-time data integration
- Memory-constrained environments
- Python-native workflows
- Ad-hoc cross-system queries

**Not for:**

- All data in same database (use direct SQL - 10-100x faster)
- Need GROUP BY or aggregations (use database)
- Maximum performance for same-database queries (use database)
- Distributed processing (use Spark/Flink)

---

## 🎯 Start Here: The Most Secure Way

### Step 1: Install and Basic Setup

```bash
pip install streaming-sql-engine
```

### Step 2: Use the Default Configuration (Most Stable)

**This is the safest way to start** - it handles all edge cases, works with any data types, and requires no special configuration:

```python
from streaming_sql_engine import Engine

# Default configuration: Most stable and reliable
engine = Engine()  # use_polars=False (default)

# Register your data sources
def postgres_users():
    # Your PostgreSQL connection code
    for row in cursor:
        yield {"id": row[0], "name": row[1]}

def mysql_orders():
    # Your MySQL connection code
    for row in cursor:
        yield {"id": row[0], "user_id": row[1], "total": row[2]}

engine.register("users", postgres_users)
engine.register("orders", mysql_orders)

# Write SQL queries
query = """
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
    WHERE orders.total > 100
"""

# Execute and iterate results
for row in engine.query(query):
    print(row)
```

**Why This Configuration is Best to Start:**

- **Most Stable**: Handles mixed data types gracefully
- **No Schema Errors**: No type inference issues
- **Works Everywhere**: No external dependencies required
- **Reliable**: Battle-tested Python code
- **Fast for Small-Medium Data**: Excellent performance for typical use cases

**Use this when:**

- You're just getting started
- Your datasets are < 100K rows
- You have mixed data types
- You need maximum reliability
- Polars is not available

---

## Two Stable Join Options

The engine provides two stable join algorithms that work reliably with any data:

### Option 1: Lookup Join (Default)

**What it is:** Python hash-based join - the default when no special metadata is provided.

**How to use:**

```python
engine = Engine()  # use_polars=False (default)
engine.register("products", products_source)
engine.register("images", images_source)
# No special metadata - uses Lookup Join automatically
```

**How it works:**

1. Builds hash index on right side (loads all right rows into memory)
2. Streams left side row-by-row
3. Looks up matches in hash index (O(1) per lookup)

**Performance (100K products, 300K images):**

- **Rows processed:** 299,553
- **Time:** 39.63 seconds
- **Memory overhead:** 177.11 MB
- **CPU:** 2.8%
- **Throughput:** 7,559 rows/second

**When to use:**

- Default choice - works with any data
- Small to medium datasets (< 1M rows)
- When right side fits in memory
- When data is not sorted

**Pros:**

- ✅ Most compatible (works with any data types)
- ✅ No special requirements
- ✅ Reliable and stable
- ✅ Good performance for medium datasets

**Cons:**

- ⚠️ Loads entire right side into memory
- ⚠️ Not optimal for very large right tables

---

### Option 2: Merge Join (Sorted Data)

**What it is:** Streaming merge join for pre-sorted data - most memory-efficient join algorithm.

**How to use:**

```python
engine = Engine()  # use_polars=False (required for Merge Join)
engine.register("products", products_source, ordered_by="product_id")
engine.register("images", images_source, ordered_by="product_id")
# Both sides must be sorted by join key
```

**How it works:**

1. Both sides stream simultaneously (no index needed)
2. Compares join keys and advances iterators
3. When keys match, joins the rows
4. Only buffers small groups of duplicate keys

**Performance (100K products, 300K images, sorted):**

- **Rows processed:** 179,871
- **Time:** 24.79 seconds
- **Memory overhead:** 0.87 MB (lowest!)
- **CPU:** 3.5%
- **Throughput:** 7,256 rows/second

**When to use:**

- Data is already sorted (or can be sorted once)
- Memory-constrained environments
- Very large datasets (> 1M rows)
- When you want maximum memory efficiency

**Pros:**

- ✅ Lowest memory usage (O(1) - only buffers current rows)
- ✅ Fast for sorted data (O(n+m) single pass)
- ✅ True streaming (both sides stream simultaneously)
- ✅ Can handle datasets larger than RAM

**Cons:**

- ⚠️ Requires pre-sorted data
- ⚠️ Must specify `ordered_by` metadata
- ⚠️ Requires `use_polars=False`

**Example: Preparing Data for Merge Join**

```python
# Step 1: Sort your JSONL files
# Use the provided utility:
python examples/sort_jsonl.py products.jsonl products_sorted.jsonl product_id
python examples/sort_jsonl.py images.jsonl images_sorted.jsonl product_id

# Step 2: Use sorted files with Merge Join
engine = Engine(use_polars=False)
engine.register("products", lambda: load_jsonl("products_sorted.jsonl"), ordered_by="product_id")
engine.register("images", lambda: load_jsonl("images_sorted.jsonl"), ordered_by="product_id")

# Step 3: Query - Merge Join will be used automatically
query = """
    SELECT products.product_id, products.title, images.image
    FROM products
    LEFT JOIN images ON products.product_id = images.product_id
"""
```

**Sample Data Structure:**

For Merge Join to work, your data must be sorted. Example:

**products.jsonl (sorted by product_id):**

```jsonl
{"product_id": 1, "title": "Product 1", "checked": 1}
{"product_id": 2, "title": "Product 2", "checked": 1}
{"product_id": 3, "title": "Product 3", "checked": 0}
{"product_id": 4, "title": "Product 4", "checked": 1}
```

**images.jsonl (sorted by product_id):**

```jsonl
{"product_id": 1, "image": "img1.jpg", "image_type": "main"}
{"product_id": 1, "image": "img1_alt.jpg", "image_type": "thumbnail"}
{"product_id": 2, "image": "img2.jpg", "image_type": "main"}
{"product_id": 4, "image": "img4_1.jpg", "image_type": "main"}
{"product_id": 4, "image": "img4_2.jpg", "image_type": "gallery"}
```

**Result:** Merge Join processes both files simultaneously, comparing `product_id` values and joining matching rows. Memory usage stays constant regardless of file size.

---

## Experimenting with Options

Once you're comfortable with the basics, you can experiment with different options to optimize for your specific use case.

### Option 1: Enable Debug Mode

See what's happening under the hood:

```python
engine = Engine(debug=True)  # Shows execution details
```

**Output:**

```
============================================================
STREAMING SQL ENGINE - DEBUG MODE
============================================================

[1/3] PARSING SQL QUERY...
SQL parsed successfully

[2/3] BUILDING LOGICAL PLAN...
Logical plan built

[3/3] EXECUTING QUERY...
  Using LOOKUP JOIN (building index...)
```

**Performance Impact:** Negligible - debug output only, no performance penalty.

---

### Option 2: Enable Polars (For Large Datasets)

**When to use**: Large datasets (> 100K rows), consistent data types

```python
engine = Engine(use_polars=True)  # Enable Polars for speed
```

**Benefits:**

- Faster for large datasets (vectorized operations)
- SIMD acceleration
- Better for consistent schemas

**Trade-offs:**

- Requires data normalization (consistent types)
- Can fail on mixed types
- Requires Polars dependency

**Performance (100K products, 300K images):**

- **Rows processed:** 299,553
- **Time:** 39.36 seconds
- **Memory overhead:** 197.64 MB
- **CPU:** 3.8%
- **Throughput:** 7,610 rows/second

**Example:**

```python
engine = Engine(use_polars=True)

# Make sure your data has consistent types
def normalized_source():
    for row in raw_source():
        yield {
            "id": int(row.get("id", 0)),
            "price": float(row.get("price", 0.0)),
            "name": str(row.get("name", "")),
        }

engine.register("products", normalized_source)
```

**When to use:**

- Large datasets (> 100K rows)
- Consistent data types
- Speed is priority
- Polars is available

**Pros:**

- ✅ Fast for large datasets (vectorized)
- ✅ SIMD acceleration
- ✅ Good throughput

**Cons:**

- ⚠️ Requires data normalization
- ⚠️ Higher memory usage
- ⚠️ Can fail on mixed types

---

### Option 3: Enable MMAP (For Large Files)

**When to use**: Large files (> 100MB), memory-constrained systems

```python
engine = Engine(use_polars=False)  # MMAP requires use_polars=False
engine.register("products", source, filename="products.jsonl")  # MMAP enabled
```

**Benefits:**

- 90-99% memory reduction
- Works with files larger than RAM
- OS-managed memory mapping

**Trade-offs:**

- Requires file-based sources
- Slower for small files (overhead)
- Requires `use_polars=False`

**Performance (100K products, 300K images):**

- **Rows processed:** 100,000
- **Time:** 19.65 seconds
- **Memory overhead:** 43.50 MB (77% less than Lookup Join!)
- **CPU:** 3.5%
- **Throughput:** 5,090 rows/second

**Example:**

```python
engine = Engine(use_polars=False)  # MMAP requires use_polars=False

def jsonl_source():
    with open("products.jsonl", "r") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

engine.register("products", jsonl_source, filename="products.jsonl")
```

**When to use:**

- Large files (> 100MB)
- Memory-constrained systems
- Files larger than available RAM
- When memory is priority

**Pros:**

- ✅ 90-99% memory reduction
- ✅ Can handle files larger than RAM
- ✅ OS-managed memory

**Cons:**

- ⚠️ Requires file-based sources
- ⚠️ Slower for small files
- ⚠️ Requires `use_polars=False`

**Note:** MMAP Join can use Polars internally for faster index building, but the join algorithm itself is MMAP (not Polars Join).

---

### Option 4: Polars + Column Pruning

**When to use**: Wide tables with many columns, only need a few columns

```python
engine = Engine(use_polars=True)

def optimized_source(dynamic_columns=None):
    # Only read requested columns
    if dynamic_columns:
        columns = dynamic_columns
    else:
        columns = ["id", "name", "price", "description", "category", ...]  # All columns

    for row in read_data(columns):
        yield row

engine.register("products", optimized_source)
```

**Performance (100K products, 300K images):**

- **Rows processed:** 299,553
- **Time:** 37.72 seconds (5% faster than Polars alone)
- **Memory overhead:** 164.27 MB (17% less than Polars alone)
- **CPU:** 1.8%
- **Throughput:** 7,942 rows/second (highest throughput!)

**What You Get:**

- Reduced I/O (only reads needed columns)
- Faster queries (less data to process)
- Lower memory usage

**When to use:**

- Wide tables (many columns)
- Only need subset of columns
- Want to reduce I/O and memory

**Pros:**

- ✅ Highest throughput (7,942 rows/s)
- ✅ Reduced I/O
- ✅ Lower memory usage

**Cons:**

- ⚠️ Requires protocol support in source function
- ⚠️ Requires Polars

---

### Option 5: Polars + Filter Pushdown

**When to use**: Queries that filter most rows, want early filtering

```python
engine = Engine(use_polars=True)

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Apply WHERE clause at source level
    query = "SELECT * FROM products"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"

    for row in execute_query(query):
        yield row

engine.register("products", optimized_source)
```

**Performance (100K products, 300K images):**

- **Rows processed:** 299,553
- **Time:** 40.95 seconds
- **Memory overhead:** 150.18 MB (24% less than Polars alone)
- **CPU:** 4.7%
- **Throughput:** 7,315 rows/second

**What You Get:**

- Early filtering (reduces data volume)
- Faster execution (less data to process)
- Lower memory usage

**When to use:**

- Queries filter most rows
- Want to reduce data transfer
- Source supports WHERE clause

**Pros:**

- ✅ Early filtering
- ✅ Reduced data volume
- ✅ Lower memory usage

**Cons:**

- ⚠️ Requires protocol support in source function
- ⚠️ Requires source to support WHERE clause

---

### Option 6: All Optimizations Combined

**The Ultimate Configuration** for maximum performance:

```python
engine = Engine(use_polars=True, first_match_only=True)

def ultimate_source(dynamic_where=None, dynamic_columns=None):
    """
    Source with all optimizations:
    - Filter pushdown (dynamic_where)
    - Column pruning (dynamic_columns)
    - Data normalization (for Polars)
    """
    # Build optimized query
    query = build_query(dynamic_where, dynamic_columns)

    for row in execute_query(query):
        # Normalize types for Polars stability
        yield normalize_types(row)

engine.register("products", ultimate_source)
```

**Performance (100K products, 300K images):**

- **Rows processed:** 100,000 (reduced by first_match_only)
- **Time:** 16.15 seconds (fastest!)
- **Memory overhead:** 38.41 MB (78% less than Polars alone)
- **CPU:** 2.2%
- **Throughput:** 6,191 rows/second

**What You Get:**

- Polars Join (speed)
- Column Pruning (I/O)
- Filter Pushdown (early filtering)
- First Match Only (prevents Cartesian products)

**Best for:** Very large datasets (> 1M rows) when speed is priority

**Note:** This uses Polars Join, not MMAP Join. For memory-constrained scenarios, use `use_polars=False` with `filename` parameter instead.

**When to use:**

- Very large datasets (> 1M rows)
- Speed is priority
- Want all optimizations
- Can normalize data types

**Pros:**

- ✅ Fastest execution time (16.15s)
- ✅ Low memory overhead (38.41 MB)
- ✅ All optimizations combined

**Cons:**

- ⚠️ Requires protocol support
- ⚠️ Requires data normalization
- ⚠️ Requires Polars

---

## Performance Comparison Table

Based on benchmark results with **100K products** and **300K images** (100K products × ~3 images each):

| Configuration                     | Rows Processed | Time (s)  | Memory Overhead (MB) | CPU % | Throughput (rows/s) |
| --------------------------------- | -------------- | --------- | -------------------- | ----- | ------------------- |
| **1. Merge Join (Sorted)**        | 179,871        | 24.79     | **0.87**             | 3.5   | 7,256               |
| **2. Lookup Join (Default)**      | 299,553        | 39.63     | 177.11               | 2.8   | 7,559               |
| **3. Polars Join**                | 299,553        | 39.36     | 197.64               | 3.8   | 7,610               |
| **4. MMAP Join**                  | 100,000        | 19.65     | 43.50                | 3.5   | 5,090               |
| **5. Polars + Column Pruning**    | 299,553        | 37.72     | 164.27               | 1.8   | **7,942**           |
| **6. Polars + Filter Pushdown**   | 299,553        | 40.95     | 150.18               | 4.7   | 7,315               |
| **7. All Optimizations Combined** | 100,000        | **16.15** | 38.41                | 2.2   | 6,191               |

### Key Insights

**Fastest Execution:** All Optimizations Combined (16.15s)

- Uses Polars Join + Column Pruning + Filter Pushdown + first_match_only
- Best for speed priority

**Lowest Memory:** Merge Join (0.87 MB)

- True streaming, no index needed
- Best for memory-constrained environments

**Highest Throughput:** Polars + Column Pruning (7,942 rows/s)

- Vectorized operations + reduced I/O
- Best for processing large volumes

**Best Balance:** MMAP Join (19.65s, 43.50 MB)

- Good speed with low memory
- Best for large files when memory matters

---

## Performance Guide

### By Dataset Size

| Size              | Configuration                   | Why                                       |
| ----------------- | ------------------------------- | ----------------------------------------- |
| **< 10K rows**    | `use_polars=False` (default)    | Fastest, most stable                      |
| **10K-100K rows** | `use_polars=False` (default)    | Still fastest, handles mixed types        |
| **100K-1M rows**  | `use_polars=True` OR `filename` | Polars Join (speed) OR MMAP Join (memory) |
| **> 1M rows**     | All optimizations               | Maximum performance                       |

### By Priority

**Priority: Stability** - Use default (`use_polars=False`)

```python
engine = Engine()  # Most stable
```

**Performance:** 39.63s, 177.11 MB memory, 7,559 rows/s

**Priority: Speed** - Use Polars

```python
engine = Engine(use_polars=True)  # Fastest for large datasets
```

**Performance:** 39.36s, 197.64 MB memory, 7,610 rows/s

**Priority: Memory** - Use MMAP

```python
engine = Engine()
engine.register("table", source, filename="data.jsonl")  # Lowest memory
```

**Performance:** 19.65s, 43.50 MB memory, 5,090 rows/s

**Priority: Both** - Choose based on priority:

**If speed is more important:**

```python
engine = Engine(use_polars=True)  # Uses Polars Join (fastest)
engine.register("table", source)  # No filename - Polars Join
```

**Performance:** 39.36s, 197.64 MB memory, 7,610 rows/s

**If memory is more important:**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join (lowest memory)
engine.register("table", source, filename="data.jsonl")  # MMAP Join
```

**Performance:** 19.65s, 43.50 MB memory, 5,090 rows/s

**Note:** Polars Join and MMAP Join are mutually exclusive - the engine chooses one based on `use_polars` flag. MMAP Join can use Polars internally for index building, but the join algorithm itself is MMAP.

---

## Learning Path

### Level 1: Beginner (Start Here)

```python
# Most stable configuration
engine = Engine()  # Default: use_polars=False
engine.register("table1", source1)
engine.register("table2", source2)
```

**Learn:**

- Basic source registration
- Simple SQL queries
- How joins work

**Performance:** 39.63s, 177.11 MB memory, 7,559 rows/s

---

### Level 2: Intermediate

```python
# Add debug mode to see what's happening
engine = Engine(debug=True)

# Experiment with Polars for large datasets
engine = Engine(use_polars=True)
```

**Learn:**

- Debug output
- When to use Polars
- Data normalization

**Performance:** 39.36s, 197.64 MB memory, 7,610 rows/s

---

### Level 3: Advanced

```python
# Use MMAP for large files (requires use_polars=False)
engine = Engine(use_polars=False)  # MMAP Join requires use_polars=False
engine.register("table", source, filename="data.jsonl")

# Use Merge Join for sorted data
engine.register("table", source, ordered_by="key")
```

**Learn:**

- MMAP for memory efficiency
- Merge Join for sorted data
- Protocol optimizations

**Performance:**

- MMAP: 19.65s, 43.50 MB memory, 5,090 rows/s
- Merge Join: 24.79s, 0.87 MB memory, 7,256 rows/s

---

### Level 4: Expert

```python
# All optimizations combined
engine = Engine(use_polars=True, first_match_only=True)

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Filter pushdown + Column pruning
    pass

engine.register("table", optimized_source)
```

**Learn:**

- Protocol-based optimizations
- Combining all options
- Maximum performance tuning

**Performance:** 16.15s, 38.41 MB memory, 6,191 rows/s

---

## Common Pitfalls

### Pitfall 1: Using Polars Without Normalization

**Problem:**

```python
engine = Engine(use_polars=True)
# Mixed types cause schema inference errors
```

**Solution:**

```python
def normalized_source():
    for row in raw_source():
        yield {
            "id": int(row.get("id", 0)),
            "price": float(row.get("price", 0.0)),
        }
```

---

### Pitfall 2: Using MMAP Without Polars (Very Slow)

**Problem:**

```python
engine = Engine(use_polars=False)
engine.register("table", source, filename="data.jsonl")  # Very slow!
```

**Solution:**

```python
# MMAP uses Polars internally for index building if available
# But you still need use_polars=False for MMAP Join algorithm
engine = Engine(use_polars=False)  # MMAP Join requires this
engine.register("table", source, filename="data.jsonl")
# MMAP will use Polars internally for faster index building
```

---

### Pitfall 3: Using MMAP for Small Files

**Problem:**

```python
# MMAP overhead > benefit for small files
engine.register("table", source, filename="small.jsonl")  # Slower!
```

**Solution:**

```python
# No filename for small files
engine.register("table", source)  # Faster for < 100MB
```

---

## Quick Decision Guide

- **Just starting?** Use default (`Engine()`) - **39.63s, 177.11 MB**
- **Have large datasets?** Use `use_polars=True` - **39.36s, 197.64 MB**
- **Memory constrained?** Use `filename` parameter (MMAP) - **19.65s, 43.50 MB**
- **Data is sorted?** Use `ordered_by` parameter (Merge Join) - **24.79s, 0.87 MB**
- **Want maximum performance?** Use `use_polars=True` + protocols - **16.15s, 38.41 MB**

---

## Real-World Example: Complete Workflow

### Step 1: Start Simple (Most Secure)

```python
from streaming_sql_engine import Engine

# Start with default (most stable)
engine = Engine()

def postgres_users():
    # Your PostgreSQL code
    pass

def mysql_orders():
    # Your MySQL code
    pass

engine.register("users", postgres_users)
engine.register("orders", mysql_orders)

results = engine.query("SELECT * FROM users JOIN orders ON users.id = orders.user_id")
```

**Performance:** 39.63s, 177.11 MB memory, 7,559 rows/s

### Step 2: Add Debug Mode (Understand What's Happening)

```python
engine = Engine(debug=True)  # See execution details
```

### Step 3: Optimize for Your Use Case

**If you have large datasets:**

```python
engine = Engine(use_polars=True)  # Enable Polars
```

**Performance:** 39.36s, 197.64 MB memory, 7,610 rows/s

**If you have large files:**

```python
engine = Engine(use_polars=False)  # MMAP Join requires use_polars=False
engine.register("table", source, filename="data.jsonl")  # Enable MMAP
```

**Performance:** 19.65s, 43.50 MB memory, 5,090 rows/s

**If you have sorted data:**

```python
engine.register("table", source, ordered_by="key")  # Enable Merge Join
```

**Performance:** 24.79s, 0.87 MB memory, 7,256 rows/s

### Step 4: Combine Optimizations

**For Speed Priority (Polars Join):**

```python
engine = Engine(use_polars=True)  # Uses Polars Join

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Supports all optimizations
    pass

engine.register("table", optimized_source)  # No filename - Polars Join
```

**Performance:** 16.15s, 38.41 MB memory, 6,191 rows/s

**For Memory Priority (MMAP Join):**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Supports all optimizations
    pass

engine.register("table", optimized_source, filename="data.jsonl")  # MMAP Join
```

**Performance:** 19.65s, 43.50 MB memory, 5,090 rows/s

---

## Summary

### Start Here (Most Secure)

```python
engine = Engine()  # Default: use_polars=False
engine.register("table1", source1)
engine.register("table2", source2)
```

**Why:** Most stable, handles all edge cases, works with any data types

**Performance:** 39.63s, 177.11 MB memory, 7,559 rows/s

---

### Then Experiment

1. **Add debug mode**: `Engine(debug=True)` - See what's happening
2. **Try Polars**: `Engine(use_polars=True)` - For large datasets (39.36s, 197.64 MB)
3. **Try MMAP**: `filename="data.jsonl"` - For large files (19.65s, 43.50 MB)
4. **Try Merge Join**: `ordered_by="key"` - For sorted data (24.79s, 0.87 MB)

---

### Advanced: Mix Options

**Best Mix for Large Files:**

**Option 1: Speed Priority (Polars Join)**

```python
engine = Engine(use_polars=True)  # Uses Polars Join (fastest)
engine.register("table", source)  # No filename needed
```

**Performance:** 39.36s, 197.64 MB memory, 7,610 rows/s

**Option 2: Memory Priority (MMAP Join)**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join (lowest memory)
engine.register("table", source, filename="data.jsonl")  # MMAP enabled
```

**Performance:** 19.65s, 43.50 MB memory, 5,090 rows/s

**Best Mix for Maximum Performance:**

**Option 1: Speed Priority (Polars Join + Protocols)**

```python
engine = Engine(use_polars=True)  # Uses Polars Join

def source(dynamic_where=None, dynamic_columns=None):
    # All optimizations (filter pushdown + column pruning)
    pass

engine.register("table", source)  # No filename - Polars Join
```

**Performance:** 16.15s, 38.41 MB memory, 6,191 rows/s

**Option 2: Memory Priority (MMAP Join + Protocols)**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join

def source(dynamic_where=None, dynamic_columns=None):
    # All optimizations (filter pushdown + column pruning)
    pass

engine.register("table", source, filename="data.jsonl")  # MMAP Join
```

**Performance:** 19.65s, 43.50 MB memory, 5,090 rows/s

---

## Key Takeaways

1. **Start Simple**: Use default configuration (`Engine()`) - it's the most stable (39.63s, 177.11 MB)
2. **Experiment Gradually**: Add options one at a time to understand their impact
3. **Mix Wisely**: Choose Polars Join (speed) OR MMAP Join (memory) based on priority
4. **Know When to Use Each**:
   - Small files: default (39.63s, 177.11 MB)
   - Large files: Polars Join (39.36s, 197.64 MB) OR MMAP Join (19.65s, 43.50 MB)
   - Sorted data: Merge Join (24.79s, 0.87 MB)
   - Maximum performance: All optimizations (16.15s, 38.41 MB)

---

**Remember**: Start with the default configuration, then experiment with options as you understand your data and performance needs better.

## Getting Started

Installation:

```bash
pip install streaming-sql-engine
```

Quick start:

```python
from streaming_sql_engine import Engine

engine = Engine()

# Register data sources (any Python function that returns an iterator)
def users_source():
    return iter([
        {"id": 1, "name": "Alice", "dept_id": 10},
        {"id": 2, "name": "Bob", "dept_id": 20},
    ])

def departments_source():
    return iter([
        {"id": 10, "name": "Engineering"},
        {"id": 20, "name": "Sales"},
    ])

engine.register("users", users_source)
engine.register("departments", departments_source)

# Execute SQL query
query = """
    SELECT users.name, departments.name AS dept
    FROM users
    JOIN departments ON users.dept_id = departments.id
"""

for row in engine.query(query):
    print(row)
# Output:
# {'users.name': 'Alice', 'departments.name': 'Engineering'}
# {'users.name': 'Bob', 'departments.name': 'Sales'}
```

**For database connections**, create iterator functions:

```python
from streaming_sql_engine import Engine
import psycopg2

engine = Engine()

# Register database table (iterator function)
def users_source():
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE active = true")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "email": row[2]}
    conn.close()

engine.register("users", users_source)

# Query
for row in engine.query("SELECT * FROM users WHERE users.active = true"):
    print(row)
```

---

## Conclusion

The Streaming SQL Engine fills a unique niche: **cross-system data integration**. While it may not match the raw performance of specialized tools for their specific use cases, it excels at joining data from different systems - a problem that traditional databases cannot solve.

**Key strengths:**

- Cross-system joins (databases, APIs, files)
- Zero infrastructure requirements
- Memory-efficient streaming architecture
- Python-native integration
- Automatic optimizations
- Simple deployment

**Best suited for:**

- Microservices data aggregation
- Cross-system ETL pipelines
- Real-time data integration
- Memory-constrained environments
- Python-native workflows

For cross-system data integration, the Streaming SQL Engine provides a unique solution that balances performance, simplicity, and flexibility.

---

## Resources

- **PyPI:** `pip install streaming-sql-engine`
