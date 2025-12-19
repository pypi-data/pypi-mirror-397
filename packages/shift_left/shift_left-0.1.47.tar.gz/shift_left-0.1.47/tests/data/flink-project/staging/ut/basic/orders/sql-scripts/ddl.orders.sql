CREATE TABLE IF NOT EXISTS orders (
    customer_id STRING,
    order_amount_sum DECIMAL(20, 2),
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    PRIMARY KEY (customer_id) NOT ENFORCED
) DISTRIBUTED BY HASH(customer_id) INTO 1 BUCKETS WITH (
    'value.format' = 'json-registry',
    'value.fields-include' = 'all',
    'scan.startup.mode' = 'earliest-offset',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded',
    'value.json-registry.schema-context' = '.flink-dev',
    'key.json-registry.schema-context' = '.flink-dev'
);