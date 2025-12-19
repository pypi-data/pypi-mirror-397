INSERT INTO kpi_config_table
SELECT 
    dbtable,
    MAX(CASE WHEN rn = 1 THEN kpiname END) AS kpiname,
    MAX(CASE WHEN rn = 1 THEN kpistatus END) AS kpistatus,
    MAX(CASE WHEN rn = 1 THEN networkservice END) AS networkservice,
    MAX(CASE WHEN rn = 1 THEN elementtype END) AS elementtype,
    MAX(CASE WHEN rn = 1 THEN interfacename END) AS interfacename
FROM (
    SELECT dbtable, kpiname, kpistatus, networkservice, elementtype, interfacename,
           ROW_NUMBER() OVER (PARTITION BY dbtable ORDER BY `time` DESC) as rn
    FROM basic_table_stream
) WHERE rn = 1
GROUP BY dbtable;