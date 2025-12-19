CREATE TABLE IF NOT EXISTS etf_hub_users_t (
    return_id STRING,
    employee_id STRING,
    employee_ssn STRING,
    tax_year BIGINT,
    business_id STRING,
    submission_details ROW<tax_year BIGINT>,
    return_data ROW<business MAP<STRING, STRING>, employee ROW<employee_id STRING, ssn STRING>>, 
    structured ROW<submission_details ROW<tax_year BIGINT>, return_data ROW<business MAP<STRING, STRING>, employee ROW<employee_id STRING, ssn STRING>>>,
    PRIMARY KEY (return_id) NOT ENFORCED
) DISTRIBUTED BY HASH(return_id) INTO 3 BUCKETS WITH (
    'changelog.mode' = 'append',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded',
    'scan.startup.mode' = 'earliest-offset',
    'value.fields-include' = 'all',
    'key.format' = 'avro-registry',
    'value.format' = 'avro-registry',
    'key.avro-registry.schema-context' = '.flink-dev',
    'value.avro-registry.schema-context' = '.flink-dev'
);