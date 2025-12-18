CREATE SCHEMA IF NOT EXISTS dw_core;

CREATE TABLE IF NOT EXISTS dw_core.schema_version (
    version      VARCHAR(32)    NOT NULL,
    applied_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    applied_by   VARCHAR(128)   DEFAULT CURRENT_USER,
    PRIMARY KEY (version)
);

-- Core promotion table for d_promotion_3_0
CREATE TABLE IF NOT EXISTS dw_core.d_promotion_3_0 (
    promotionid VARCHAR(255) PRIMARY KEY,
    promotioncode VARCHAR(255),
    promotiondescription TEXT,
    promotiontype VARCHAR(50),
    promotionstartdate TIMESTAMP,
    promotionenddate TIMESTAMP,
    couponmin INT,
    couponmax INT,
    promotionskus TEXT,
    excld_promo_sku TEXT,
    promo_elements TEXT,
    tieredskus TEXT,
    excld_tier_sku TEXT,
    bundleskus TEXT,
    excld_bundle_sku TEXT,
    discount_sku TEXT,
    discount_excld_sku TEXT,
    discountinfo TEXT,
    key VARCHAR(255),
    uniquepromoflag BOOLEAN,
    sitewideflag BOOLEAN,
    prepaidflag BOOLEAN,
    personalizedpromoflag BOOLEAN,
    marketinitiative VARCHAR(255),
    partnerid VARCHAR(255),
    program VARCHAR(255),
    campaigntype VARCHAR(255),
    campaignname VARCHAR(255),
    vertical VARCHAR(255),
    mediatype VARCHAR(255),
    marketingbranch VARCHAR(255),
    eventinstime TIMESTAMP,
    eventupdtime TIMESTAMP,
    dailystarttime TIME,
    dailyendtime TIME,
    limitsglobal BIGINT,
    limitsorder BIGINT,
    limitscustomer BIGINT,
    deliverymethod VARCHAR(255),
    deliveryoption VARCHAR(255),
    sourcegroups TEXT,
    skuspurchasetype VARCHAR(255),
    purchasetype VARCHAR(255),
    redemptionmethod VARCHAR(255),
    tags TEXT,
    minimumpurchase DECIMAL(10,2),
    maximumdiscounted DECIMAL(10,2),
    promo_properties TEXT,
    periscopeid VARCHAR(255),
    dwcreatedby VARCHAR(255),
    dwcreatedat TIMESTAMP,
    etl_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    etl_created_by VARCHAR(255)
);

CREATE TABLE dw_core.example_table (
    id   INT PRIMARY KEY,
    name VARCHAR(100)
);

INSERT INTO dw_core.schema_version (version, applied_at)
VALUES ('1.0', CURRENT_TIMESTAMP);