import pandas as pd
import sqlite3
import time
import numpy as np

def setup_data_warehouse():
    """设置测试用的数据仓库环境"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # 创建维度表
    cursor.execute('''
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT,
            year INTEGER,
            quarter INTEGER,
            month INTEGER,
            month_name TEXT,
            day INTEGER,
            weekday INTEGER,
            weekday_name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE dim_product (
            product_key INTEGER PRIMARY KEY,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            subcategory TEXT,
            price REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE dim_store (
            store_key INTEGER PRIMARY KEY,
            store_id TEXT,
            store_name TEXT,
            region TEXT,
            city TEXT,
            state TEXT
        )
    ''')
    
    # 创建事实表
    cursor.execute('''
        CREATE TABLE fact_sales (
            sales_key INTEGER PRIMARY KEY,
            date_key INTEGER,
            product_key INTEGER,
            store_key INTEGER,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
            FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
            FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
        )
    ''')
    
    # 插入维度数据
    # 日期维度
    date_data = []
    for year in range(2022, 2024):
        for month in range(1, 13):
            # 简化处理，每个月30天
            for day in range(1, 31):
                date_key = year * 10000 + month * 100 + day
                weekday = (day + month * 2 + year % 100 + (year % 100) // 4 + 
                          (year // 100) // 4 + 5 * (year // 100)) % 7
                weekday_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                               'Friday', 'Saturday', 'Sunday'][weekday]
                month_name = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December'][month-1]
                date_data.append((date_key, f"{year}-{month:02d}-{day:02d}", 
                                year, (month-1)//3+1, month, month_name, 
                                day, weekday, weekday_name))
    cursor.executemany(
        "INSERT INTO dim_date VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        date_data
    )
    
    # 产品维度
    product_data = [
        (1, 'P001', 'Laptop XPS 13', 'Electronics', 'Computers', 1200.00),
        (2, 'P002', 'iPhone 13', 'Electronics', 'Mobile Phones', 800.00),
        (3, 'P003', 'Samsung Galaxy S22', 'Electronics', 'Mobile Phones', 750.00),
        (4, 'P004', 'Dell Monitor 27"', 'Electronics', 'Accessories', 300.00),
        (5, 'P005', 'Sony WH-1000XM5', 'Electronics', 'Audio', 350.00),
        (6, 'P006', 'Nike Air Max', 'Fashion', 'Shoes', 150.00),
        (7, 'P007', 'Levi\'s Jeans', 'Fashion', 'Clothing', 80.00),
        (8, 'P008', 'Adidas T-Shirt', 'Fashion', 'Clothing', 30.00),
        (9, 'P009', 'Kitchen Blender', 'Home Appliances', 'Kitchen', 60.00),
        (10, 'P010', 'Hair Dryer', 'Home Appliances', 'Personal Care', 40.00)
    ]
    cursor.executemany(
        "INSERT INTO dim_product VALUES (?, ?, ?, ?, ?, ?)",
        product_data
    )
    
    # 商店维度
    store_data = [
        (1, 'S001', 'Downtown Store', 'North', 'New York', 'NY'),
        (2, 'S002', 'Westside Mall', 'West', 'Los Angeles', 'CA'),
        (3, 'S003', 'Southside Plaza', 'South', 'Houston', 'TX'),
        (4, 'S004', 'East End Market', 'East', 'Miami', 'FL'),
        (5, 'S005', 'Midwest Center', 'Central', 'Chicago', 'IL')
    ]
    cursor.executemany(
        "INSERT INTO dim_store VALUES (?, ?, ?, ?, ?, ?)",
        store_data
    )
    
    # 插入事实表数据
    fact_data = []
    for i in range(10000):
        sales_key = i + 1
        date_key = np.random.choice([d[0] for d in date_data])
        product_key = np.random.randint(1, 11)
        store_key = np.random.randint(1, 6)
        quantity = np.random.randint(1, 10)
        unit_price = float(product_data[product_key-1][5])
        total_amount = quantity * unit_price
        fact_data.append((sales_key, date_key, product_key, store_key, quantity, unit_price, total_amount))
    
    cursor.executemany(
        "INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?)",
        fact_data
    )
    
    conn.commit()
    return conn

def test_2dimensional_query(conn):
    """测试二维查询"""
    print("=== 测试二维查询（产品类别 vs 地区）===")
    query = """
        SELECT
            dp.category,
            ds.region,
            SUM(fs.total_amount) as total_sales,
            COUNT(*) as transaction_count
        FROM
            fact_sales fs
        JOIN
            dim_product dp ON fs.product_key = dp.product_key
        JOIN
            dim_store ds ON fs.store_key = ds.store_key
        GROUP BY
            dp.category, ds.region
        ORDER BY
            dp.category, ds.region
    """
    
    start_time = time.time()
    result = pd.read_sql_query(query, conn)
    execution_time = time.time() - start_time
    
    print(f"查询执行时间: {execution_time:.4f} 秒")
    print("查询结果预览:")
    print(result.head(10))
    
    # 验证结果正确性
    assert len(result) > 0, "查询结果为空"
    assert "total_sales" in result.columns, "结果缺少必要列"
    
    return result

def test_time_series_analysis(conn):
    """测试时间序列分析查询"""
    print("=== 测试时间序列分析（月度销售趋势）===")
    query = """
        SELECT
            dd.year,
            dd.month,
            dd.month_name,
            SUM(fs.total_amount) as monthly_sales,
            COUNT(DISTINCT fs.product_key) as unique_products_sold,
            SUM(fs.quantity) as total_units_sold
        FROM
            fact_sales fs
        JOIN
            dim_date dd ON fs.date_key = dd.date_key
        WHERE
            dd.year = 2023
        GROUP BY
            dd.year, dd.month, dd.month_name
        ORDER BY
            dd.month
    """
    
    start_time = time.time()
    result = pd.read_sql_query(query, conn)
    execution_time = time.time() - start_time
    
    print(f"查询执行时间: {execution_time:.4f} 秒")
    print("查询结果预览:")
    print(result)
    
    # 验证结果正确性
    assert len(result) == 12, "应为12个月的数据"
    assert result["month"].min() == 1 and result["month"].max() == 12, "月份范围不正确"
    
    return result

def test_drill_down_analysis(conn):
    """测试下钻分析查询"""
    print("=== 测试下钻分析（从类别到子类别）===")
    # 先获取类别总销售额
    category_query = """
        SELECT
            dp.category,
            SUM(fs.total_amount) as total_sales
        FROM
            fact_sales fs
        JOIN
            dim_product dp ON fs.product_key = dp.product_key
        GROUP BY
            dp.category
        ORDER BY
            total_sales DESC
    """
    
    # 再获取子类别的销售额
    subcategory_query = """
        SELECT
            dp.category,
            dp.subcategory,
            SUM(fs.total_amount) as total_sales
        FROM
            fact_sales fs
        JOIN
            dim_product dp ON fs.product_key = dp.product_key
        GROUP BY
            dp.category, dp.subcategory
        ORDER BY
            dp.category, total_sales DESC
    """
    
    category_result = pd.read_sql_query(category_query, conn)
    subcategory_result = pd.read_sql_query(subcategory_query, conn)
    
    print("类别级销售额:")
    print(category_result)
    print("\n子类别级销售额（下钻）:")
    print(subcategory_result)
    
    # 验证下钻的正确性 - 类别销售额应等于其子类别销售额之和
    for category in category_result["category"]:
        category_total = category_result[category_result["category"] == category]["total_sales"].values[0]
        subcategories_total = subcategory_result[subcategory_result["category"] == category]["total_sales"].sum()
        
        assert abs(category_total - subcategories_total) < 0.01, \
            f"下钻数据不一致: {category}类别的总和应为{category_total}，但子类别的总和为{subcategories_total}"
    
    print("下钻分析数据一致性验证通过")
    return category_result, subcategory_result

def test_complex_filtered_query(conn):
    """测试复杂条件过滤查询"""
    print("=== 测试复杂条件过滤查询 ===")
    query = """
        SELECT
            dp.category,
            ds.city,
            dd.quarter,
            SUM(fs.total_amount) as total_sales,
            AVG(fs.total_amount) as avg_transaction_value,
            COUNT(*) as transaction_count
        FROM
            fact_sales fs
        JOIN
            dim_product dp ON fs.product_key = dp.product_key
        JOIN
            dim_store ds ON fs.store_key = ds.store_key
        JOIN
            dim_date dd ON fs.date_key = dd.date_key
        WHERE
            dd.year = 2023
            AND dp.category IN ('Electronics', 'Fashion')
            AND fs.total_amount > 100
            AND dd.weekday_name NOT IN ('Saturday', 'Sunday')
        GROUP BY
            dp.category, ds.city, dd.quarter
        HAVING
            COUNT(*) > 10
        ORDER BY
            total_sales DESC
    """
    
    start_time = time.time()
    result = pd.read_sql_query(query, conn)
    execution_time = time.time() - start_time
    
    print(f"查询执行时间: {execution_time:.4f} 秒")
    print(f"复杂过滤查询返回 {len(result)} 条记录")
    print("查询结果预览:")
    print(result.head(10))
    
    return result

def test_performance_scaling(conn):
    """测试查询性能扩展性"""
    print("=== 测试查询性能扩展性 ===")
    
    queries = [
        ("简单聚合查询", """
            SELECT 
                SUM(total_amount) as total_sales 
            FROM fact_sales
        """),
        ("两表连接查询", """
            SELECT 
                dp.category, 
                SUM(fs.total_amount) as category_sales 
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_key = dp.product_key
            GROUP BY dp.category
        """),
        ("三表连接查询", """
            SELECT 
                dp.category, 
                ds.region,
                SUM(fs.total_amount) as sales 
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_key = dp.product_key
            JOIN dim_store ds ON fs.store_key = ds.store_key
            JOIN dim_date dd ON fs.date_key = dd.date_key
            WHERE dd.year = 2023
            GROUP BY dp.category, ds.region
        """),
        ("复杂分析查询", """
            SELECT 
                dp.category,
                ds.region,
                dd.quarter,
                SUM(fs.total_amount) as total_sales,
                COUNT(DISTINCT fs.sales_key) as transaction_count,
                SUM(fs.quantity) as units_sold,
                AVG(fs.unit_price) as avg_unit_price
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_key = dp.product_key
            JOIN dim_store ds ON fs.store_key = ds.store_key
            JOIN dim_date dd ON fs.date_key = dd.date_key
            WHERE dd.year = 2023
            GROUP BY dp.category, ds.region, dd.quarter
            ORDER BY total_sales DESC
        """)
    ]
    
    performance_results = []
    
    for query_name, query_sql in queries:
        times = []
        for _ in range(5):  # 运行多次取平均
            start_time = time.time()
            pd.read_sql_query(query_sql, conn)
            times.append(time.time() - start_time)
        
        avg_time = sum(times) / len(times)
        performance_results.append((query_name, avg_time))
        print(f"{query_name}: 平均执行时间 {avg_time:.4f} 秒")
    
    return performance_results

# 运行测试
if __name__ == "__main__":
    print("设置测试数据仓库...")
    conn = setup_data_warehouse()
    
    print("\n开始多维查询测试...\n")
    test_2dimensional_query(conn)
    print("\n")
    test_time_series_analysis(conn)
    print("\n")
    test_drill_down_analysis(conn)
    print("\n")
    test_complex_filtered_query(conn)
    print("\n")
    test_performance_scaling(conn)
    
    print("\n所有测试完成！")
    conn.close()
