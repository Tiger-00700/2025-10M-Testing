-- 准备关联表
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    region VARCHAR(50)
);

-- 测试1：内连接查询
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date, o.total_amount, c.name, c.region
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE c.region = '华东' AND o.order_date > '2023-01-01'
ORDER BY o.total_amount DESC
LIMIT 100;

-- 测试2：复杂多表连接
EXPLAIN ANALYZE
SELECT o.order_id, o.total_amount, c.name, p.product_name, i.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items i ON o.order_id = i.order_id
JOIN products p ON i.product_id = p.product_id
WHERE c.region = '华北' AND o.status = 'completed'
GROUP BY o.order_id
HAVING SUM(i.quantity) > 10
ORDER BY o.total_amount DESC;
