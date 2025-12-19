INSERT INTO form_w2_t
SELECT 
    form_w2_id,
    MAX_BY(return_id, `time`) AS return_id,
    MAX_BY(employee_id, `time`) AS employee_id,
    MAX_BY(employee_ssn, `time`) AS employee_ssn
FROM form_w2
GROUP BY form_w2_id;