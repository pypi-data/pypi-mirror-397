from typing import Dict, Any
from datetime import datetime
from pyspark.sql import Row

from dwh.data.schema_data_builder import SchemaDataBuilder


class DiscountTiersBuilder:
    """Builder for discount_discountTiers nested structure"""
    
    def __init__(self):
        self.tiered_skus = [{"skuOrCategoryId": "TIER1_SKU"}]
        self.excluded_skus = [{"skuOrCategoryId": "EXCLUDED_TIER_SKU"}]
        self.periscope_ids = ["PERISCOPE_001"]
    
    def with_tiered_skus(self, *skus: str) -> 'DiscountTiersBuilder':
        self.tiered_skus = [{"skuOrCategoryId": sku} for sku in skus]
        return self
    
    def with_excluded_skus(self, *skus: str) -> 'DiscountTiersBuilder':
        self.excluded_skus = [{"skuOrCategoryId": sku} for sku in skus]
        return self
    
    def to_dict(self) -> Row:
        return Row(
            tieredSkus=[Row(skuOrCategoryId=sku["skuOrCategoryId"]) for sku in self.tiered_skus],
            excludedTieredSkus=[Row(skuOrCategoryId=sku["skuOrCategoryId"]) for sku in self.excluded_skus],
            periscopeId=self.periscope_ids
        )


class BundleBuilder:
    """Builder for bundle nested structures"""
    
    def __init__(self, bundle_name: str = "DEFAULT"):
        self.bundle_name = bundle_name
        self.promotion_skus = [{"skuOrCategoryId": f"{bundle_name}_SKU"}]
        self.excluded_skus = [{"skuOrCategoryId": f"{bundle_name}_EXCLUDED"}]
        self.minimum_purchase = 1
        self.maximum_discounted = 1
    
    def with_promotion_skus(self, *skus: str) -> 'BundleBuilder':
        self.promotion_skus = [{"skuOrCategoryId": sku} for sku in skus]
        return self
    
    def with_excluded_skus(self, *skus: str) -> 'BundleBuilder':
        self.excluded_skus = [{"skuOrCategoryId": sku} for sku in skus]
        return self
    
    def with_limits(self, min_purchase: int, max_discounted: int) -> 'BundleBuilder':
        self.minimum_purchase = min_purchase
        self.maximum_discounted = max_discounted
        return self
    
    def to_dict(self) -> Row:
        return Row(
            promotionSkus=[Row(skuOrCategoryId=sku["skuOrCategoryId"]) for sku in self.promotion_skus],
            excludedSkus=[Row(skuOrCategoryId=sku["skuOrCategoryId"]) for sku in self.excluded_skus],
            minimumpurchase=self.minimum_purchase,
            maximumDiscounted=self.maximum_discounted
        )


class PromotionDataBuilder(SchemaDataBuilder):
    """
    Data builder for promotion schema (ecom_sflycompromotion_promotions)
    
    This builder provides a fluent interface for creating schema-compliant promotion records
    with built-in validation of allowable data values and formats.
    
    VALIDATION BENEFITS:
    - Enforces valid promotion types (PERCENTAGE_DISCOUNT, FIXED_DISCOUNT, BOGO, etc.)
    - Validates ISO date formats for schedule dates
    - Ensures coupon limits are positive integers
    - Documents expected tag categories and metadata values
    - Provides type safety for complex nested structures
    - Schema validation against real DDL files
    
    USAGE EXAMPLES:
    
    # Basic promotion creation
    promo = (PromotionDataBuilder(schema_service)
             .with_id("PROMO_BLACK_FRIDAY_001")
             .with_name("Black Friday Electronics Sale")
             .with_promotion_type("PERCENTAGE_DISCOUNT")
             .with_tags("BLACK_FRIDAY", "ELECTRONICS", "SEASONAL"))
    
    # Template-based variations
    base_promo = PromotionDataBuilder(schema_service).with_id("PROMO_BASE")
    variations = [
        base_promo.with_schedule_end_date("2025-01-01T13:15:00.000Z").to_records(),
        base_promo.with_schedule_end_date("2025-01-01T13:20:00.000Z").to_records()
    ]
    
    # Complex nested objects with sub-builders
    discount_tiers = (DiscountTiersBuilder()
                      .with_tiered_skus("ELECTRONICS_TV", "ELECTRONICS_LAPTOP")
                      .with_excluded_skus("CLEARANCE_ITEMS"))
    
    promo_with_tiers = base_promo.with_discount_tiers(discount_tiers)
    
    # Generate parquet files
    records = promo_with_tiers.to_records()
    DataSerializer.to_parquet(records, "/path/to/output.parquet", spark, schema)
    
    EXPECTED DATA VALUES:
    - promotion_type: PERCENTAGE_DISCOUNT | FIXED_DISCOUNT | BOGO | FREE_SHIPPING
    - tags: BLACK_FRIDAY | SUMMER | ELECTRONICS | CLOTHING | SEASONAL | CLEARANCE
    - redemption_method: AUTOMATIC | MANUAL | CODE_REQUIRED
    - campaign_types: SEASONAL_DISCOUNT | FLASH_SALE | LOYALTY_REWARD | NEW_CUSTOMER
    - verticals: ELECTRONICS | CLOTHING | HOME | BOOKS | SPORTS
    - media_types: DIGITAL_DISPLAY | EMAIL | SOCIAL | SEARCH | TV | RADIO
    
    SCHEMA VALIDATION:
    - Uses real DDL files via schema_service
    - Validates all records against production schema on to_records()
    - Ensures schema compliance before data serialization
    - Catches schema evolution issues early in development
    """
    
    def __init__(self, schema_service):
        super().__init__(schema_service)
    
    @property
    def schema_ref(self) -> str:
        """Return the schema reference for promotion data"""
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        return LoadPromosSchema.SOURCE_SCHEMA_REF
    
    @property
    def table_name(self) -> str:
        """Return the table name for promotion data"""
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        return LoadPromosSchema.SOURCE_TABLE_NAME

    def create_default_record(self) -> Dict[str, Any]:
        """Create a default promotion record with all required fields"""

        bundle_a = BundleBuilder("BUNDLE_A").with_promotion_skus("SKU123").with_limits(10, 100)
        tiers = DiscountTiersBuilder().with_tiered_skus("ELECTRONICS_TV", "ELECTRONICS_LAPTOP")

        return {
            "_id": "PROMO_DEFAULT_001",
            "name": "Default Test Promotion",
            "description": "Default test promotion for schema validation",
            "properties_promotionType": "PERCENTAGE_DISCOUNT",
            "schedule_startDate": datetime(2023, 11, 24, 0, 0, 0),
            "schedule_endDate": datetime(2023, 11, 27, 23, 59, 59),
            "createDate": datetime(2023, 11, 1, 10, 30, 0),
            "updatedate": datetime(2023, 11, 15, 14, 45, 0),
            "couponmin": 1,
            "couponmax": 10,
            "skus_promotionSkus": [Row(skuOrCategoryId="DEFAULT_SKU")],
            "skus_excludedSkus": [Row(skuOrCategoryId="EXCLUDED_SKU")],
            "skus_minimumPurchase": 100,
            "skus_maximumDiscounted": 5,
            "skus_purchaseType": "QUANTITY_BASED",
            # "discount_discountTiers": DiscountTiersBuilder().to_dict(),
            "discount_discountTiers": tiers.to_dict(),
            "discount_purchaseType": "TIERED_DISCOUNT",
            # "bundles_bundleA": BundleBuilder("BUNDLE_A").with_limits(2, 1).to_dict(),
            "bundles_bundleA": bundle_a.to_dict(),
            "bundles_bundleB": BundleBuilder("BUNDLE_B").to_dict(),
            "bundles_bundleC": BundleBuilder("BUNDLE_C").to_dict(),
            "bundles_bundleD": BundleBuilder("BUNDLE_D").to_dict(),
            "bundles_discountY": Row(
                promotionSkus=[Row(skuOrCategoryId="DISCOUNT_Y_SKU")],
                excludedSkus=[Row(skuOrCategoryId="DISCOUNT_Y_EXCLUDED")]
            ),
            "properties_redemptionMethod": "AUTOMATIC",
            "properties_periscopeId": "PERISCOPE_DEFAULT_001",
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
            "properties_fields_key": "DEFAULT_KEY",
            "tags": ["DEFAULT", "TEST", "PROMOTION"],
            "deliveryMethod": ["STANDARD_SHIPPING"],
            "deliveryOption": ["HOME_DELIVERY"],
            "sourceGroups": ["TEST_GROUP"],
            "metaData_MARKETING_INITIATIVE": "DEFAULT_INITIATIVE",
            "metaData_PARTNER": "DEFAULT_PARTNER",
            "metaData_PROGRAM": "DEFAULT_PROGRAM",
            "metaData_CAMPAIGN_TYPE": "DEFAULT_CAMPAIGN",
            "metaData_CAMPAIGN_NAME": "DEFAULT_CAMPAIGN_NAME",
            "metaData_VERTICAL": "DEFAULT_VERTICAL",
            "metaData_MEDIA_TYPE": "DEFAULT_MEDIA",
            "metaData_MARKETING_BRANCH": "DEFAULT_BRANCH",
            "schedule_dailyStartTime": 0,
            "schedule_dailyEndTime": 86399,
            "limits_global": 10000,
            "limits_order": 5,
            "limits_customer": 2,
            "nestedShipping_promotionType": "FREE_SHIPPING_THRESHOLD",
            "ptn_ingress_date": "2023-11-24"
        }
    
    def with_id(self, promotion_id: str) -> 'PromotionDataBuilder':
        """Set promotion ID"""
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["_id"] = promotion_id
        return new_builder
    
    def with_name(self, name: str) -> 'PromotionDataBuilder':
        """Set promotion name"""
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["name"] = name
        return new_builder
    
    def with_schedule_end_date(self, end_date: str) -> 'PromotionDataBuilder':
        """Set schedule end date (ISO format: 2025-01-01T13:15:00.000Z)"""
        new_builder = self._ensure_record_copy()
        if end_date.endswith('Z'):
            end_date = end_date[:-1] + '+00:00'
        new_builder.records[-1]["schedule_endDate"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        return new_builder
    
    def with_promotion_type(self, promo_type: str) -> 'PromotionDataBuilder':
        """Set promotion type with validation"""
        valid_types = {"PERCENTAGE_DISCOUNT", "FIXED_DISCOUNT", "BOGO", "FREE_SHIPPING", "TIERED_DISCOUNT"}
        if promo_type not in valid_types:
            raise ValueError(f"Invalid promotion type '{promo_type}'. Valid types: {valid_types}")
        
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["properties_promotionType"] = promo_type
        return new_builder
    
    def with_tags(self, *tags: str) -> 'PromotionDataBuilder':
        """Set promotion tags for categorization and filtering"""
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["tags"] = list(tags)
        return new_builder
    
    def with_redemption_method(self, method: str) -> 'PromotionDataBuilder':
        """Set redemption method (AUTOMATIC, MANUAL, CODE_REQUIRED)"""
        valid_methods = {"AUTOMATIC", "MANUAL", "CODE_REQUIRED"}
        if method not in valid_methods:
            raise ValueError(f"Invalid redemption method '{method}'. Valid methods: {valid_methods}")
        
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["properties_redemptionMethod"] = method
        return new_builder
    
    def with_coupon_limits(self, min_count: int, max_count: int) -> 'PromotionDataBuilder':
        """Set coupon usage limits"""
        if min_count < 0 or max_count < 0:
            raise ValueError("Coupon limits must be positive integers")
        if min_count > max_count:
            raise ValueError("Minimum coupon count cannot exceed maximum")
        
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["couponmin"] = min_count
        new_builder.records[-1]["couponmax"] = max_count
        return new_builder
    
    def with_discount_tiers(self, tiers_builder: DiscountTiersBuilder) -> 'PromotionDataBuilder':
        """Set discount tiers using builder"""
        new_builder = self._ensure_record_copy()
        new_builder.records[-1]["discount_discountTiers"] = tiers_builder.to_dict()
        return new_builder
    
    def with_bundle(self, bundle_key: str, bundle_builder: BundleBuilder) -> 'PromotionDataBuilder':
        """Set bundle using builder (e.g., 'bundles_bundleA')"""
        new_builder = self._ensure_record_copy()
        new_builder.records[-1][bundle_key] = bundle_builder.to_dict()
        return new_builder
