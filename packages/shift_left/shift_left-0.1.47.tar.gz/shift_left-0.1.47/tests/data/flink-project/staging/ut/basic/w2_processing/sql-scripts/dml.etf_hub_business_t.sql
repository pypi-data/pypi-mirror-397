INSERT INTO etf_hub_business_t
SELECT 
    business_id,
    MAX(dba_name) AS dba_name,
    MAX(user_id) AS user_id,
    MAX(recipient_id) AS recipient_id,
    MAX(email_address) AS email_address
FROM (
    SELECT business_id, dba_name, user_id, recipient_id, email_address,
           ROW_NUMBER() OVER (PARTITION BY business_id ORDER BY `time` DESC) as rn
    FROM etf_hub_business
) WHERE rn = 1
GROUP BY business_id;