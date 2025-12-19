INSERT INTO orders
SELECT 
    customer_id,
    SUM(order_amount) as order_amount_sum,
    window_start,
    window_end
FROM TABLE(TUMBLE(TABLE daily_spend, DESCRIPTOR($rowtime), INTERVAL '24' HOUR))
WHERE order_amount <> 0
GROUP BY customer_id, window_start, window_end;