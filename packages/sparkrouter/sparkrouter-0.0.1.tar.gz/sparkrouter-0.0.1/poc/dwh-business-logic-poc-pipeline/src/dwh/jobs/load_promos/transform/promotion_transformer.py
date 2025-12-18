from pyspark.sql import DataFrame
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    col, lit, when, array_contains, current_timestamp, coalesce,
    array_join, transform, size, concat, row_number,
    concat_ws
)
from pyspark.sql.types import IntegerType


class PromotionTransformer:
    """Handles flattening nested structures and business rule application"""
    
    def __init__(self, schema_service, debug_schemas: bool = False):
        self.debug_schemas = debug_schemas
        self.schema_service = schema_service

    def transform(self, df: DataFrame, created_by: str) -> DataFrame:
        """Transform parquet data to PostgreSQL schema with business rules"""
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} INPUT SCHEMA ===")
            df.printSchema()
            print(f"Row count: {df.count()}")
        
        transformed_df = self._transform_to_postgres_schema(df, created_by)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} OUTPUT SCHEMA ===")
            transformed_df.printSchema()
            print(f"Row count: {transformed_df.count()}")

        # Apply deduplication business rule
        window_spec = Window.partitionBy("promotionid").orderBy(col("eventupdtime").desc())
        final_df = transformed_df.withColumn("rn", row_number().over(window_spec)).filter(col("rn") == 1).drop("rn")
        
        # Enforce exact target schema
        final_df = self._enforce_target_schema(final_df)
        
        if self.debug_schemas:
            print(f"\n=== {self.__class__.__name__} FINAL SCHEMA (after deduplication) ===")
            final_df.printSchema()
            print(f"Final row count: {final_df.count()}")
        
        return final_df

    def _transform_to_postgres_schema(self, df, created_by):
        """Transform parquet DataFrame to PostgreSQL schema"""
        return (
            df.distinct()
            .withColumn("promotionid", col("_id"))
            .withColumn("promotion_code", col("name"))
            .withColumn("promotiondescription", col("description"))
            .withColumn("promotiontype", col("properties_promotionType"))
            .withColumn("promotionstartdate", col("schedule_startDate").cast("timestamp"))
            .withColumn("promotionenddate", col("schedule_endDate").cast("timestamp"))
            .withColumn("couponmin", col("couponmin").cast(IntegerType()))
            .withColumn("couponmax", col("couponmax").cast(IntegerType()))
            .withColumn("promotionskus", self._extract_sku_list("skus_promotionSkus"))
            .withColumn("excld_promo_sku", self._extract_sku_list("skus_excludedSkus"))
            .withColumn("promo_elements", lit("DEFAULT_PROMO_ELEMENTS"))
            .withColumn("tieredskus", self._extract_tiered_skus("tieredSkus"))
            .withColumn("excld_tier_sku", self._extract_tiered_skus("excludedTieredSkus"))
            .withColumn("bundleskus", self._extract_bundle_skus("promotionSkus"))
            .withColumn("excld_bundle_sku", self._extract_bundle_skus("excludedSkus"))
            .withColumn("discount_sku", self._extract_sku_list("bundles_discountY.promotionSkus"))
            .withColumn("discount_excld_sku", self._extract_sku_list("bundles_discountY.excludedSkus"))
            .withColumn("discountinfo", col("nestedShipping_promotionType"))
            .withColumn("key", col("properties_fields_key"))
            .withColumn("uniquepromoflag", lit(False))
            .withColumn("sitewideflag",
                        when((col("properties_redemptionMethod") == "QualifyingPurchase")
                             & array_contains(col("tags"), "salePricePromo"), True).otherwise(False))
            .withColumn("prepaidflag", lit(False))
            .withColumn("personalizedpromoflag", lit(False))
            .withColumn("marketinitiative", col("metaData_MARKETING_INITIATIVE"))
            .withColumn("partnerid", col("metaData_PARTNER"))
            .withColumn("program", col("metaData_PROGRAM"))
            .withColumn("campaigntype", col("metaData_CAMPAIGN_TYPE"))
            .withColumn("campaignname", col("metaData_CAMPAIGN_NAME"))
            .withColumn("vertical", col("metaData_VERTICAL"))
            .withColumn("mediatype", col("metaData_MEDIA_TYPE"))
            .withColumn("marketingbranch", col("metaData_MARKETING_BRANCH"))
            .withColumn("eventinstime", col("createDate").cast("timestamp"))
            .withColumn("eventupdtime", col("updatedate").cast("timestamp"))
            .withColumn("dailystarttime", col("schedule_dailyStartTime").cast("string"))
            .withColumn("dailyendtime", col("schedule_dailyEndTime").cast("string"))
            .withColumn("limitsglobal", col("limits_global").cast("bigint"))
            .withColumn("limitsorder", col("limits_order").cast("bigint"))
            .withColumn("limitscustomer", col("limits_customer").cast("bigint"))
            .withColumn("deliverymethod", self._extract_array_as_string("deliveryMethod"))
            .withColumn("deliveryoption", self._extract_array_as_string("deliveryOption"))
            .withColumn("sourcegroups", self._extract_array_as_string("sourceGroups"))
            .withColumn("skuspurchasetype", col("skus_purchaseType"))
            .withColumn("purchasetype", col("discount_purchaseType"))
            .withColumn("redemptionmethod", col("properties_redemptionMethod"))
            .withColumn("tags", self._extract_array_as_string("tags", "|"))
            .withColumn("minimumpurchase", self._extract_minimum_purchase().cast("decimal(10,2)"))
            .withColumn("maximumdiscounted", self._extract_maximum_discounted().cast("decimal(10,2)"))
            .withColumn("promo_properties", self._extract_properties_flags())
            .withColumn("periscopeid", coalesce(col("properties_periscopeId"),
                                                self._extract_array_as_string("discount_discountTiers.periscopeId")))
            .withColumn("dwcreatedby", lit(created_by))
            .withColumn("dwcreatedat", current_timestamp())
            .withColumn("etl_created_at", current_timestamp())
            .withColumn("etl_created_by", lit(created_by))
            .select(
                "promotionid", "promotioncode", "promotiondescription", "promotiontype",
                "promotionstartdate", "promotionenddate", "couponmin", "couponmax", "promotionskus", "excld_promo_sku",
                "promo_elements", "tieredskus", "excld_tier_sku", "bundleskus", "excld_bundle_sku",
                "discount_sku", "discount_excld_sku", "discountinfo", "key", "uniquepromoflag",
                "sitewideflag", "prepaidflag", "personalizedpromoflag", "marketinitiative", "partnerid", "program",
                "campaigntype", "campaignname", "vertical", "mediatype", "marketingbranch",
                "eventinstime", "eventupdtime", "dailystarttime", "dailyendtime",
                "limitsglobal", "limitsorder", "limitscustomer", "deliverymethod", "deliveryoption",
                "sourcegroups", "skuspurchasetype", "purchasetype", "redemptionmethod", "tags",
                "minimumpurchase", "maximumdiscounted", "promo_properties", "periscopeid",
                "dwcreatedby", "dwcreatedat", "etl_created_at", "etl_created_by"
            )
        )

    def _extract_sku_list(self, column_path):
        return when(
            array_join(transform(col(column_path), lambda x: x.skuOrCategoryId), ",") == "",
            lit(None).cast("string")
        ).otherwise(
            array_join(transform(col(column_path), lambda x: x.skuOrCategoryId), ",")
        )

    def _extract_tiered_skus(self, field_name):
        return when(
            (size(col(f"discount_discountTiers.{field_name}")) == 0)
            | (array_join(transform(col(f"discount_discountTiers.{field_name}"), lambda x: x.skuOrCategoryId),
                          ",") == ""),
            lit(None).cast("string")
        ).otherwise(
            array_join(transform(col(f"discount_discountTiers.{field_name}"), lambda x: x.skuOrCategoryId),
                       ",")
        )

    def _extract_bundle_skus(self, field_name):
        bundle_a = when(size(col(f"bundles_bundleA.{field_name}")) > 0,
                        array_join(transform(col(f"bundles_bundleA.{field_name}"), lambda x: x.skuOrCategoryId),
                                   ",")).otherwise(lit(""))
        bundle_b = when(size(col(f"bundles_bundleB.{field_name}")) > 0,
                        concat(lit(","),
                               array_join(transform(col(f"bundles_bundleB.{field_name}"), lambda x: x.skuOrCategoryId),
                                          ","))).otherwise(lit(""))
        bundle_c = when(size(col(f"bundles_bundleC.{field_name}")) > 0,
                        concat(lit(","),
                               array_join(transform(col(f"bundles_bundleC.{field_name}"), lambda x: x.skuOrCategoryId),
                                          ","))).otherwise(lit(""))
        bundle_d = when(size(col(f"bundles_bundleD.{field_name}")) > 0,
                        concat(lit(","),
                               array_join(transform(col(f"bundles_bundleD.{field_name}"), lambda x: x.skuOrCategoryId),
                                          ","))).otherwise(lit(""))

        concatenated = concat(bundle_a, bundle_b, bundle_c, bundle_d)
        return when(concatenated == "", lit(None).cast("string")).otherwise(concatenated)

    def _extract_array_as_string(self, column_path, separator=","):
        return when(
            array_join(col(column_path), separator) == "",
            lit(None).cast("string")
        ).otherwise(
            array_join(col(column_path), separator)
        )

    def _extract_minimum_purchase(self):
        return coalesce(
            col("bundles_bundleA.minimumpurchase"),
            col("bundles_bundleB.minimumpurchase"),
            col("bundles_bundleC.minimumpurchase"),
            col("bundles_bundleD.minimumpurchase"),
            col("skus_minimumPurchase")
        )

    def _extract_maximum_discounted(self):
        return coalesce(
            col("bundles_bundleA.maximumDiscounted"),
            col("bundles_bundleB.maximumDiscounted"),
            col("bundles_bundleC.maximumDiscounted"),
            col("bundles_bundleD.maximumDiscounted"),
            col("skus_maximumDiscounted")
        )

    def _extract_properties_flags(self):
        return when(
            col("properties_flags").isNull(),
            lit(None).cast("string")
        ).otherwise(
            concat_ws(", ",
                      concat(lit("bxgyl: "), coalesce(col("properties_flags.bxgyl").cast("string"), lit("false"))),
                      concat(lit("chargeShippingFee: "),
                             coalesce(col("properties_flags.chargeShippingFee").cast("string"), lit("true"))),
                      concat(lit("codeUnique: "),
                             coalesce(col("properties_flags.codeUnique").cast("string"), lit("false"))),
                      concat(lit("employeeOnly: "),
                             coalesce(col("properties_flags.employeeOnly").cast("string"), lit("false"))),
                      concat(lit("householdFraudCheck: "),
                             coalesce(col("properties_flags.householdFraudCheck").cast("string"), lit("false"))),
                      concat(lit("newSignUp: "),
                             coalesce(col("properties_flags.newSignUp").cast("string"), lit("false"))),
                      concat(lit("newUserOnly: "),
                             coalesce(col("properties_flags.newUserOnly").cast("string"), lit("false"))),
                      concat(lit("postPurchase: "),
                             coalesce(col("properties_flags.postPurchase").cast("string"), lit("false"))),
                      concat(lit("showOnSite: "),
                             coalesce(col("properties_flags.showOnSite").cast("string"), lit("false")))
                      )
        )
    
    def _enforce_target_schema(self, df: DataFrame) -> DataFrame:
        """Enforce exact target schema types using schema service"""
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        
        target_schema = self.schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        
        # Create DataFrame with exact target schema
        return df.sparkSession.createDataFrame(df.rdd, target_schema)
