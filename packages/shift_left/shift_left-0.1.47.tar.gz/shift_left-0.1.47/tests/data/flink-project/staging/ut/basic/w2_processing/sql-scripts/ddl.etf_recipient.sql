CREATE TABLE IF NOT EXISTS etf_recipient (
    recipient_id INT,
    email_address STRING,
    recipient_telephone_no STRING,
    fax_number STRING,
    PRIMARY KEY (recipient_id) NOT ENFORCED
) DISTRIBUTED BY HASH(recipient_id) INTO 3 BUCKETS WITH (
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