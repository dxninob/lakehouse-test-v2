CREATE EXTERNAL SCHEMA IF NOT EXISTS curated_data
FROM DATA CATALOG
DATABASE 'lakehouse-curated-data'
IAM_ROLE 'arn:aws:iam::<AWS-id>:role/<role-name>';


CREATE MATERIALIZED VIEW view_1 AS
SELECT * FROM curated_data.table_1;

CREATE MATERIALIZED VIEW view_2 AS
SELECT * FROM curated_data.table_2;

CREATE VIEW view_3 AS
SELECT * FROM curated_data.table_3
WITH NO SCHEMA BINDING;

CREATE VIEW view_4 AS
SELECT * FROM curated_data.table_4
WITH NO SCHEMA BINDING;

CREATE VIEW view_5 AS
SELECT * FROM curated_data.table_5
WITH NO SCHEMA BINDING;


CREATE DATASHARE lakehouseshare;
ALTER DATASHARE lakehouseshare ADD SCHEMA schema_name;
ALTER DATASHARE lakehouseshare SET PUBLICACCESSIBLE TRUE;
GRANT SHARE ON DATASHARE lakehouseshare TO PUBLIC;