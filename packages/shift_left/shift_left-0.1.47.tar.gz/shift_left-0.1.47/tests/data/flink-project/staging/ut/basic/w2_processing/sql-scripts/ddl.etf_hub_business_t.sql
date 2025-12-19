CREATE TABLE IF NOT EXISTS etf_hub_business_t (
    business_id STRING,
    dba_name STRING,
    user_id STRING,
    recipient_id STRING,
    email_address STRING,
    PRIMARY KEY (business_id) NOT ENFORCED
) DISTRIBUTED BY HASH(business_id) INTO 3 BUCKETS WITH (
    'key.format' = 'avro-registry',
    'value.format' = 'avro-registry',
    'key.avro-registry.schema-context' = '.flink-dev',
    'value.avro-registry.schema-context' = '.flink-dev',
    'value.fields-include' = 'all',
    'scan.startup.mode' = 'earliest-offset',
    'changelog.mode' = 'append',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded'
);