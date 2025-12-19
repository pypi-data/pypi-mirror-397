CREATE TABLE IF NOT EXISTS kpi_config_table (
    dbtable STRING,
    kpiname STRING,
    kpistatus STRING,
    networkservice STRING,
    elementtype STRING,
    interfacename STRING,
    PRIMARY KEY (dbtable) NOT ENFORCED
) DISTRIBUTED BY HASH(dbtable) INTO 1 BUCKETS WITH (
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