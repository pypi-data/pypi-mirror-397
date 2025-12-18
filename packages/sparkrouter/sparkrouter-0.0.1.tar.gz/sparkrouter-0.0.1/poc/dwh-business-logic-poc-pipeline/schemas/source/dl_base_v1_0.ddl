-- Parquet table structure for ecom_sflycompromotion_promotions
CREATE TABLE IF NOT EXISTS ecom_sflycompromotion_promotions (
    -- Raw input columns from parquet
    _id VARCHAR(255),
    name VARCHAR(255),
    description TEXT,
    properties_promotionType VARCHAR(50),
    schedule_startDate TIMESTAMP,
    schedule_endDate TIMESTAMP,
    createDate TIMESTAMP,
    couponmin INT,
    couponmax INT,
    
    -- Nested array columns for SKUs
    skus_promotionSkus ARRAY<STRUCT<skuOrCategoryId: STRING>>,
    skus_excludedSkus ARRAY<STRUCT<skuOrCategoryId: STRING>>,
    skus_minimumPurchase INT,
    skus_maximumDiscounted INT,
    skus_purchaseType VARCHAR(255),
    
    -- Nested discount tiers
    discount_discountTiers STRUCT<
        tieredSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        excludedTieredSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        periscopeId: ARRAY<STRING>
    >,
    discount_purchaseType VARCHAR(255),
    
    -- Bundle structures
    bundles_bundleA STRUCT<
        promotionSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        excludedSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        minimumpurchase: INT,
        maximumDiscounted: INT
    >,
    bundles_bundleB STRUCT<
        promotionSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        excludedSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        minimumpurchase: INT,
        maximumDiscounted: INT
    >,
    bundles_bundleC STRUCT<
        promotionSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        excludedSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        minimumpurchase: INT,
        maximumDiscounted: INT
    >,
    bundles_bundleD STRUCT<
        promotionSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        excludedSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        minimumpurchase: INT,
        maximumDiscounted: INT
    >,
    bundles_discountY STRUCT<
        promotionSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
        excludedSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>
    >,
    
    -- Properties
    properties_redemptionMethod VARCHAR(255),
    properties_periscopeId VARCHAR(255),
    properties_flags STRUCT<
        bxgyl: BOOLEAN,
        chargeShippingFee: BOOLEAN,
        codeUnique: BOOLEAN,
        employeeOnly: BOOLEAN,
        householdFraudCheck: BOOLEAN,
        newSignUp: BOOLEAN,
        newUserOnly: BOOLEAN,
        postPurchase: BOOLEAN,
        showOnSite: BOOLEAN
    >,
    properties_fields_key VARCHAR(255),
    
    -- Array columns
    tags ARRAY<STRING>,
    deliveryMethod ARRAY<STRING>,
    deliveryOption ARRAY<STRING>,
    sourceGroups ARRAY<STRING>,
    
    -- Metadata columns (camelCase with metaData prefix)
    metaData_MARKETING_INITIATIVE VARCHAR(255),
    metaData_PARTNER VARCHAR(255),
    metaData_PROGRAM VARCHAR(255),
    metaData_CAMPAIGN_TYPE VARCHAR(255),
    metaData_CAMPAIGN_NAME VARCHAR(255),
    metaData_VERTICAL VARCHAR(255),
    metaData_MEDIA_TYPE VARCHAR(255),
    metaData_MARKETING_BRANCH VARCHAR(255),
    
    -- Schedule and limits
    schedule_dailyStartTime BIGINT,
    schedule_dailyEndTime BIGINT,
    limits_global BIGINT,
    limits_order BIGINT,
    limits_customer BIGINT,
    
    -- Nested shipping
    nestedShipping_promotionType VARCHAR(255),
    
    -- Partition and ingestion metadata
    ptn_ingress_date VARCHAR(10),
    updatedate TIMESTAMP
);
