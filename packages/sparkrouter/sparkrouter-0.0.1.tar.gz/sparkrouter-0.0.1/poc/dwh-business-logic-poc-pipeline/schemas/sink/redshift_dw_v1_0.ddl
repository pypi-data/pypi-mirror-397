CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.schema_version (
    version      VARCHAR(32)    NOT NULL,
    applied_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    applied_by   VARCHAR(128)   DEFAULT CURRENT_USER,
    PRIMARY KEY (version)
);

-- CREATE TABLE dw_core.example_table (
--     id   INT PRIMARY KEY,
--     name VARCHAR(100)
-- );

INSERT INTO dw.schema_version (version)
VALUES ('1.0');