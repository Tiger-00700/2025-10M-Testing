-- 准备测试数据
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATETIME,
    total_amount DECIMAL(10,2),
    status VARCHAR(20)
);

-- 创建索引
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);

-- 插入测试数据（可使用存储过程或工具批量插入百万级数据）

-- 测试1：单条件等值查询（使用索引）
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 12345;

-- 测试2：范围查询
EXPLAIN ANALYZE
SELECT * FROM orders WHERE order_date BETWEEN '2023-01-01' AND '2023-01-31';

-- 测试3：排序操作
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id BETWEEN 10000 AND 20000
ORDER BY order_date DESC LIMIT 100;
