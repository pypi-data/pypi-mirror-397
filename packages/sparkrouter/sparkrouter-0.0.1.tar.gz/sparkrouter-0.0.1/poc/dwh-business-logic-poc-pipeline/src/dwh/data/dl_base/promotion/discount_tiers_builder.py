"""
Builder for discount tiers sub-object
"""

from typing import Dict, Any


class DiscountTiersBuilder:
    """Builder for discount_discountTiers nested object"""
    
    def __init__(self):
        self.data = {
            "tieredSkus": [],
            "excludedTieredSkus": [],
            "periscopeId": []
        }
    
    def with_tiered_skus(self, *sku_ids: str) -> 'DiscountTiersBuilder':
        """Add tiered SKUs"""
        new_builder = DiscountTiersBuilder()
        new_builder.data = self.data.copy()
        new_builder.data["tieredSkus"] = [{"skuOrCategoryId": sku} for sku in sku_ids]
        return new_builder
    
    def with_excluded_skus(self, *sku_ids: str) -> 'DiscountTiersBuilder':
        """Add excluded SKUs"""
        new_builder = DiscountTiersBuilder()
        new_builder.data = self.data.copy()
        new_builder.data["excludedTieredSkus"] = [{"skuOrCategoryId": sku} for sku in sku_ids]
        return new_builder
    
    def with_periscope_ids(self, *periscope_ids: str) -> 'DiscountTiersBuilder':
        """Add periscope IDs"""
        new_builder = DiscountTiersBuilder()
        new_builder.data = self.data.copy()
        new_builder.data["periscopeId"] = list(periscope_ids)
        return new_builder
    
    def to_record(self) -> Dict[str, Any]:
        """Get the discount tiers as a dictionary"""
        return self.data.copy()
