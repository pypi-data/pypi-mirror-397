CREATE TABLE IF NOT EXISTS etf_hub_users (
    user_id STRING,
    email_address STRING,
    contact_name STRING,
    PRIMARY KEY (user_id) NOT ENFORCED
) DISTRIBUTED BY HASH(user_id) INTO 3 BUCKETS WITH (
    'value.format' = 'avro-registry',
    'key.format' = 'avro-registry',
    'key.avro-registry.schema-context' = '.flink-dev',
    'value.avro-registry.schema-context' = '.flink-dev',
    'value.fields-include' = 'all',
    'scan.startup.mode' = 'earliest-offset',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded',
    'changelog.mode' = 'append'
);