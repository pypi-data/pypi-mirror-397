INSERT INTO etf_hub_users_t
SELECT 
    w2.return_id,
    w2.employee_id,
    w2.employee_ssn,
    returns.tax_year,
    returns.business_id,
    ROW(returns.tax_year) AS submission_details,
    ROW(MAP('businessId', returns.business_id), ROW(w2.employee_id, w2.employee_ssn)) AS return_data,
    ROW(ROW(returns.tax_year), ROW(MAP('businessId', returns.business_id), ROW(w2.employee_id, w2.employee_ssn))) AS structured
FROM form_w2_t AS w2
JOIN etf_returns_t AS returns ON w2.return_id = returns.return_id;