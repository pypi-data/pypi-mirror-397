CREATE TABLE IF NOT EXISTS daily_spend (
    `window_start` TIMESTAMP(3),
    `window_end` TIMESTAMP(3),
    PRIMARY KEY (`window_start`) NOT ENFORCED
) DISTRIBUTED BY HASH(`window_start`) INTO 1 BUCKETS WITH (
    'changelog.mode' = 'append',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded',
    'scan.startup.mode' = 'earliest-offset',
    'value.fields-include' = 'all',
    'value.json-registry.schema-context' = '.flink-dev',
    'value.format' = 'json-registry'
);