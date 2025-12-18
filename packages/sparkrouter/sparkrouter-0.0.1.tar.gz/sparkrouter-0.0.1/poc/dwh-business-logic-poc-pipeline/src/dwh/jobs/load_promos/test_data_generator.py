"""
Test data generator for LoadPromosJob

This tool helps data engineers understand the incoming data structure
and provides centralized test data generation for all test types.
"""
from pyspark.sql import SparkSession, DataFrame, Row
from dwh.services.schema.schema_service import SchemaService
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


class LoadPromosTestDataGenerator:
    """Centralized test data generator for LoadPromosJob"""

    @staticmethod
    def create_test_data(spark: SparkSession, schema_service: SchemaService, record_count: int = 2) -> DataFrame:
        """Create comprehensive test data matching the actual complex DDL schema"""
        from datetime import datetime
        
        # First create DataFrame without schema to let Spark infer, then validate against schema
        schema = schema_service.get_schema(
            LoadPromosSchema.SOURCE_SCHEMA_REF,
            LoadPromosSchema.SOURCE_TABLE_NAME
        )
        
        # Create comprehensive test data that exercises all business logic paths
        test_data = {
            # Core promotion fields
            "_id": "PROMO_TEST_001",
            "name": "Black Friday 20% Off Electronics",
            "description": "Get 20% off all electronics during Black Friday weekend. Valid on TVs, laptops, phones and accessories.",
            "properties_promotionType": "PERCENTAGE_DISCOUNT",
            
            # Schedule with realistic dates
            "schedule_startDate": datetime(2023, 11, 24, 0, 0, 0),
            "schedule_endDate": datetime(2023, 11, 27, 23, 59, 59),
            "createDate": datetime(2023, 11, 1, 10, 30, 0),

            "couponmin": 1,
            "couponmax": 10,
            "updatedate": datetime(2023, 11, 15, 14, 45, 0),
            
            # SKU arrays with realistic product data
            "skus_promotionSkus": [
                Row(skuOrCategoryId="ELECTRONICS_TV"),
                Row(skuOrCategoryId="ELECTRONICS_LAPTOP"),
                Row(skuOrCategoryId="ELECTRONICS_PHONE")
            ],
            "skus_excludedSkus": [
                Row(skuOrCategoryId="ELECTRONICS_CLEARANCE")
            ],
            "skus_minimumPurchase": 100,
            "skus_maximumDiscounted": 5,
            "skus_purchaseType": "QUANTITY_BASED",
            
            # Complex nested discount tiers
            "discount_discountTiers": Row(
                tieredSkus=[
                    Row(skuOrCategoryId="TIER1_ELECTRONICS"),
                    Row(skuOrCategoryId="TIER2_ELECTRONICS")
                ],
                excludedTieredSkus=[
                    Row(skuOrCategoryId="PREMIUM_ELECTRONICS")
                ],
                periscopeId=["PERISCOPE_001", "PERISCOPE_002"]
            ),
            "discount_purchaseType": "TIERED_DISCOUNT",
            
            # Bundle structures with realistic data
            "bundles_bundleA": Row(
                promotionSkus=[
                    Row(skuOrCategoryId="BUNDLE_A_ITEM1"),
                    Row(skuOrCategoryId="BUNDLE_A_ITEM2")
                ],
                excludedSkus=[
                    Row(skuOrCategoryId="BUNDLE_A_EXCLUDED")
                ],
                minimumpurchase=2,
                maximumDiscounted=1
            ),
            "bundles_bundleB": Row(
                promotionSkus=[
                    Row(skuOrCategoryId="BUNDLE_B_ITEM1")
                ],
                excludedSkus=[
                    Row(skuOrCategoryId="BUNDLE_B_EXCLUDED_PLACEHOLDER")
                ],
                minimumpurchase=1,
                maximumDiscounted=1
            ),
            "bundles_bundleC": Row(
                promotionSkus=[
                    Row(skuOrCategoryId="BUNDLE_C_ITEM1")
                ],
                excludedSkus=[
                    Row(skuOrCategoryId="BUNDLE_C_EXCLUDED_PLACEHOLDER")
                ],
                minimumpurchase=1,
                maximumDiscounted=1
            ),
            "bundles_bundleD": Row(
                promotionSkus=[
                    Row(skuOrCategoryId="BUNDLE_D_ITEM1")
                ],
                excludedSkus=[
                    Row(skuOrCategoryId="BUNDLE_D_EXCLUDED_PLACEHOLDER")
                ],
                minimumpurchase=1,
                maximumDiscounted=1
            ),
            "bundles_discountY": Row(
                promotionSkus=[
                    Row(skuOrCategoryId="DISCOUNT_Y_ITEM")
                ],
                excludedSkus=[
                    Row(skuOrCategoryId="DISCOUNT_Y_EXCLUDED_PLACEHOLDER")
                ]
            ),
            
            # Properties with complex flags
            "properties_redemptionMethod": "AUTOMATIC",
            "properties_periscopeId": "PERISCOPE_MAIN_001",
            "properties_flags": Row(
                bxgyl=False,
                chargeShippingFee=True,
                codeUnique=False,
                employeeOnly=False,
                householdFraudCheck=True,
                newSignUp=False,
                newUserOnly=False,
                postPurchase=False,
                showOnSite=True
            ),
            "properties_fields_key": "BLACK_FRIDAY_2023",
            
            # Array fields with realistic values
            "tags": ["BLACK_FRIDAY", "ELECTRONICS", "SEASONAL", "HIGH_VALUE"],
            "deliveryMethod": ["STANDARD_SHIPPING", "EXPRESS_SHIPPING"],
            "deliveryOption": ["HOME_DELIVERY", "STORE_PICKUP"],
            "sourceGroups": ["MARKETING_TEAM", "ELECTRONICS_CATEGORY"],
            
            # Metadata for business intelligence
            "metaData_MARKETING_INITIATIVE": "Q4_HOLIDAY_PUSH",
            "metaData_PARTNER": "ELECTRONICS_VENDOR_COOP",
            "metaData_PROGRAM": "BLACK_FRIDAY_2023",
            "metaData_CAMPAIGN_TYPE": "SEASONAL_DISCOUNT",
            "metaData_CAMPAIGN_NAME": "BF23_ELECTRONICS_20PCT",
            "metaData_VERTICAL": "ELECTRONICS",
            "metaData_MEDIA_TYPE": "DIGITAL_DISPLAY",
            "metaData_MARKETING_BRANCH": "PERFORMANCE_MARKETING",
            
            # Schedule timing (in milliseconds since midnight)
            "schedule_dailyStartTime": 0,  # Midnight
            "schedule_dailyEndTime": 86399000,  # 23:59:59
            
            # Limits for fraud prevention
            "limits_global": 10000,  # Total promotion usage limit
            "limits_order": 5,       # Max uses per order
            "limits_customer": 2,    # Max uses per customer
            
            # Nested shipping configuration
            "nestedShipping_promotionType": "FREE_SHIPPING_THRESHOLD",
            
            # Partition and ingestion metadata
            "ptn_ingress_date": "2023-11-24"
        }
        
        # Create single test record to avoid schema inference issues
        test_records = [
            Row(**test_data)
        ]
        
        # Create DataFrame and cast to match DDL schema types
        df = spark.createDataFrame(test_records)
        
        # Cast columns to match DDL schema (handles LongType -> IntegerType conversion)
        for field in schema.fields:
            if field.name in df.columns:
                df = df.withColumn(field.name, df[field.name].cast(field.dataType))
        
        return df
