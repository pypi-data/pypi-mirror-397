# Schema Management & Documentation Demo

## Schema Tracking Capabilities

### Current Schema Structure
```
ddls/
├── parquet/dl_base/dl_base_v1_0.ddl     # Source schemas
├── postgres/dl_bo/dl_bo_v1_0.ddl        # Business object schemas  
└── redshift/dw/dw_v1_0.ddl              # Data warehouse schemas
    └── dw_core/                         # With upgrade scripts
        ├── dw_core_v1_0.ddl
        ├── 001_upgrade_dw_core_v1_0_to_v1_1.sql
        └── 002_upgrade_dw_core_v1_1_to_v1_2.sql
```

### Schema Evolution Tracking
- **Version management**: Automatic detection of schema versions
- **Change tracking**: Identify added/removed/modified columns
- **Impact analysis**: Map downstream dependencies affected by changes
- **Upgrade path validation**: Ensure migration scripts are compatible

---

## Auto-Generated Documentation Example

### Promotion Schema Documentation
**Generated from**: `ddls/parquet/dl_base/dl_base_v1_0.ddl`

#### Table: ecom_sflycompromotion_promotions
**Purpose**: Stores promotion data with complex nested structures for SKUs, bundles, and discount tiers

#### Core Fields
| Field | Type | Description | Business Rules |
|-------|------|-------------|----------------|
| `_id` | VARCHAR(255) | Unique promotion identifier | Primary key, required |
| `name` | VARCHAR(255) | Promotion display name | Required for customer-facing promos |
| `description` | TEXT | Detailed promotion description | Optional, used in marketing materials |
| `properties_promotionType` | VARCHAR(50) | Type of promotion (discount, BOGO, etc.) | Must match enum values |

#### Schedule & Timing
| Field | Type | Description | Business Rules |
|-------|------|-------------|----------------|
| `schedule_startDate` | TIMESTAMP | When promotion becomes active | Must be future date for new promos |
| `schedule_endDate` | TIMESTAMP | When promotion expires | Must be after startDate |
| `schedule_dailyStartTime` | BIGINT | Daily activation time (epoch) | Optional, 24-hour format |
| `schedule_dailyEndTime` | BIGINT | Daily deactivation time (epoch) | Must be after dailyStartTime |

#### Complex Nested Structures

##### SKU Management
```sql
-- Promotion-eligible SKUs
skus_promotionSkus ARRAY<STRUCT<skuOrCategoryId: STRING>>

-- Excluded SKUs  
skus_excludedSkus ARRAY<STRUCT<skuOrCategoryId: STRING>>

-- Purchase requirements
skus_minimumPurchase INT        -- Minimum quantity required
skus_maximumDiscounted INT      -- Maximum items that get discount
skus_purchaseType VARCHAR(255)  -- Type of purchase requirement
```

##### Bundle Structures (A, B, C, D)
```sql
bundles_bundleA STRUCT<
    promotionSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
    excludedSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
    minimumpurchase: INT,
    maximumDiscounted: INT
>
```
**Business Logic**: Each bundle represents a different product grouping for complex promotions (e.g., "Buy bundle A + bundle B, get bundle C free")

##### Discount Tiers
```sql
discount_discountTiers STRUCT<
    tieredSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
    excludedTieredSkus: ARRAY<STRUCT<skuOrCategoryId: STRING>>,
    periscopeId: ARRAY<STRING>
>
```
**Business Logic**: Enables progressive discounts (e.g., "Buy 2 get 10% off, buy 5 get 20% off")

#### Feature Flags
```sql
properties_flags STRUCT<
    bxgyl: BOOLEAN,                    -- Buy X Get Y Logic
    chargeShippingFee: BOOLEAN,        -- Whether to charge shipping
    codeUnique: BOOLEAN,               -- One-time use codes
    employeeOnly: BOOLEAN,             -- Employee-exclusive promotion
    householdFraudCheck: BOOLEAN,      -- Enable fraud detection
    newSignUp: BOOLEAN,                -- New customer signup required
    newUserOnly: BOOLEAN,              -- First-time user only
    postPurchase: BOOLEAN,             -- Apply after purchase
    showOnSite: BOOLEAN                -- Display on website
>
```

#### Marketing Metadata
```sql
-- Campaign tracking fields
metaData_MARKETING_INITIATIVE VARCHAR(255)  -- Campaign initiative
metaData_PARTNER VARCHAR(255)               -- Partner name
metaData_PROGRAM VARCHAR(255)               -- Program type
metaData_CAMPAIGN_TYPE VARCHAR(255)         -- Campaign category
metaData_CAMPAIGN_NAME VARCHAR(255)         -- Specific campaign
metaData_VERTICAL VARCHAR(255)              -- Business vertical
metaData_MEDIA_TYPE VARCHAR(255)            -- Media channel
metaData_MARKETING_BRANCH VARCHAR(255)      -- Marketing branch
```

---

## Schema Dependency Mapping

### Data Flow Dependencies
```
Source: ecom_sflycompromotion_promotions (Parquet)
    ↓
Transform: promotion_transformer.py
    ├── Extracts nested SKU arrays
    ├── Flattens bundle structures  
    ├── Validates business rules
    ↓
Staging: dl_bo.promotions_staging (Postgres)
    ↓
Load: dw.promotions (Redshift)
    ├── dw.promotion_skus (normalized SKU table)
    ├── dw.promotion_bundles (bundle definitions)
    └── dw.promotion_metadata (marketing data)
```

### Impact Analysis Example
**If we add a new field to source schema:**
```sql
-- New field added to dl_base_v1_0.ddl
properties_maxUsagePerCustomer INT
```

**Automatic Impact Detection:**
1. **Source Schema**: `dl_base_v1_0.ddl` → `dl_base_v1_1.ddl`
2. **Affected Transformers**: `promotion_transformer.py` (needs update)
3. **Affected Tests**: `test_promotion_transformer.py` (schema validation will fail)
4. **Downstream Tables**: `dw.promotions` (may need new column)
5. **Documentation**: Auto-regenerated with new field

---

## Live Demo Script

### 1. Schema Change Detection
```bash
# Show current schema version
./business-logic/tools/schemas/schema-version-check.sh

# Simulate adding new field to schema
# Show framework detecting the change
# Display impact analysis report
```

### 2. Documentation Generation
```bash
# Generate documentation from current schemas
./business-logic/tools/schemas/generate-schema-docs.sh

# Show before/after when schema changes
# Demonstrate living documentation updates
```

### 3. Dependency Mapping
```bash
# Show dependency graph for promotion data flow
./business-logic/tools/schemas/show-dependencies.sh ecom_sflycompromotion_promotions

# Demonstrate impact analysis for schema change
./business-logic/tools/schemas/analyze.sh dl_base_v1_0 dl_base_v1_1
```

### 4. Version Management Demo
```bash
# Show current version deployments
./business-logic/tools/version/list-versions.sh

# Demonstrate version switching (DAG configuration change)
./business-logic/tools/version/switch-version.sh DAG_load_promos v1.0 v1.1

# Show version isolation
./business-logic/tools/version/show-isolation.sh

# Simulate instant rollback
./business-logic/tools/version/rollback.sh DAG_load_promos v1.0
```

### 5. Knowledge Repository Demo
```bash
# Simulate anomaly detection
./business-logic/tools/knowledge/simulate-anomaly.sh promotion_type "FLASH_SALE"

# Show automated business context alerts
./business-logic/tools/knowledge/show-alerts.sh

# Generate business glossary from code
./business-logic/tools/knowledge/generate-glossary.sh promotions

# Show knowledge evolution tracking
./business-logic/tools/knowledge/show-evolution.sh customer_eligibility
```

---

## Business Value Demonstration

### Current State Problems
- **Manual documentation**: Schema docs are outdated or missing
- **Unknown dependencies**: Changes break downstream systems unexpectedly  
- **Schema drift**: Production schemas diverge from development
- **Impact analysis**: Takes days to understand change implications

### Framework Solutions
- **Auto-generated docs**: Always current, generated from actual schemas
- **Dependency tracking**: Know exactly what will be affected by changes
- **Schema validation**: Prevent drift through automated testing
- **Impact analysis**: Immediate feedback on change implications

### Concrete Example
**Scenario**: Marketing wants to add customer usage limits to promotions

**Current Process**:
1. Developer adds field to schema (30 minutes)
2. Manual documentation update (2 hours)
3. Find all affected code (4-6 hours of investigation)
4. Update transformers and tests (8-12 hours)
5. Validate no breaking changes (2-4 hours)
**Total**: 16-20 hours over 2-3 days

**Framework Process**:
1. Developer adds field to DDL (30 minutes)
2. Framework generates impact analysis (automatic)
3. Documentation auto-updates (automatic)
4. Tests fail with specific guidance (immediate feedback)
5. Update transformers with schema validation (2-3 hours)
6. Deploy new version (automatic, zero MWAA changes)
**Total**: 3-4 hours same day

**Version Management Benefits**:
- **Zero MWAA changes**: DAG points to new version via config only
- **Instant rollback**: Switch back to previous version immediately
- **Parallel testing**: Run old and new versions simultaneously
- **Gradual rollout**: Deploy to subset of DAGs first

---

## Technical Implementation

### Schema Service Architecture
```python
class SchemaService:
    def get_schema_version(self, schema_name: str) -> str
    def detect_schema_changes(self, old_version: str, new_version: str) -> SchemaChanges
    def analyze_impact(self, changes: SchemaChanges) -> ImpactAnalysis
    def generate_documentation(self, schema_name: str) -> Documentation
    def validate_compatibility(self, source_schema: str, target_schema: str) -> ValidationResult
```

### Documentation Generator
```python
class DocumentationGenerator:
    def generate_table_docs(self, ddl_file: str) -> TableDocumentation
    def generate_field_docs(self, table_schema: Schema) -> FieldDocumentation  
    def generate_dependency_graph(self, schema_name: str) -> DependencyGraph
    def generate_impact_report(self, changes: SchemaChanges) -> ImpactReport
```

### Change Detection
```python
class SchemaChangeDetector:
    def compare_schemas(self, old_schema: Schema, new_schema: Schema) -> SchemaChanges
    def detect_breaking_changes(self, changes: SchemaChanges) -> List[BreakingChange]
    def suggest_migration_path(self, changes: SchemaChanges) -> MigrationPlan
```

---

## Demo Talking Points

### Key Messages
1. **"Schema management is automated, not manual"**
2. **"Documentation is always current because it's generated from code"**
3. **"Impact analysis is immediate, not a multi-day investigation"**
4. **"Schema changes are validated automatically in tests"**
5. **"Version management eliminates MWAA deployment risk"**
6. **"Rollback is instant - just change a configuration"**
7. **"Code repository becomes institutional knowledge repository"**
8. **"Anomaly detection prevents data quality surprises"**

### Show vs. Tell
- **Show**: Live schema change with immediate impact analysis
- **Show**: Auto-generated documentation updating in real-time
- **Show**: Test failures with specific guidance on what needs updating
- **Show**: Dependency graph visualization of data flow

### Business Impact
- **Time savings**: 16-20 hours → 3-4 hours for schema changes
- **Risk reduction**: No more surprise breaking changes
- **Documentation quality**: Always accurate, never outdated
- **Developer productivity**: Focus on business logic, not investigation