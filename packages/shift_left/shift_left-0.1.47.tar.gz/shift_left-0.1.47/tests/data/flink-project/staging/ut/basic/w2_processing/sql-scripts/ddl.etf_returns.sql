CREATE TABLE IF NOT EXISTS etf_returns (
    return_id BIGINT,
    tax_year STRING,
    business_id STRING,
    recipient_id INT,
    correction_type STRING,
    filing_status_id STRING,
    pdf_status BOOLEAN,
    PRIMARY KEY (return_id) NOT ENFORCED
) DISTRIBUTED BY HASH(return_id) INTO 3 BUCKETS WITH (
    'key.format' = 'avro-registry',
    'value.format' = 'avro-registry',
    'key.avro-registry.schema-context' = '.flink-dev',
    'value.avro-registry.schema-context' = '.flink-dev',
    'value.fields-include' = 'all',
    'scan.startup.mode' = 'earliest-offset',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded',
    'changelog.mode' = 'append'
);