CREATE TABLE IF NOT EXISTS w2_returns2_t (
    return_id STRING,
    employee_id STRING,
    employee_ssn STRING,
    tax_year STRING,
    business_id STRING,
    structured ROW<
        submissionDetails ROW<
            taxYear STRING
        >,
        returnData ROW<
            business MAP<STRING, STRING>,
            employee ROW<
                employeeId STRING,
                ssn STRING
            >,
            states ARRAY<STRING>
        >
    >,
    PRIMARY KEY (return_id) NOT ENFORCED
) DISTRIBUTED BY HASH(return_id) INTO 3 BUCKETS WITH (
    'changelog.mode' = 'append',
    'kafka.retention.time' = '0',
    'kafka.producer.compression.type' = 'snappy',
    'scan.bounded.mode' = 'unbounded',
    'scan.startup.mode' = 'earliest-offset',
    'value.fields-include' = 'all',
    'key.json-registry.schema-context' = '.flink-dev',
    'value.json-registry.schema-context' = '.flink-dev',
    'key.format' = 'json-registry',
    'value.format' = 'json-registry'
);