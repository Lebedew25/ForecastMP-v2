# MVP Feature Enhancement Design

## Executive Overview

This design document outlines the strategic enhancements required to transform ForecastMP-v2 from its current state into a complete MVP product aligned with the defined business requirements. The project currently has a solid technical foundation with data models, ML forecasting capabilities, and basic Wildberries/Ozon integrations, but lacks several critical user-facing features necessary for an MVP launch.

## Current State Analysis

### Existing Implementation

The project already includes:

- Multi-tenant architecture with Company and User models
- Product catalog system with marketplace mappings
- Sales transaction tracking and daily aggregation
- Inventory snapshot functionality
- ML-based forecasting using XGBoost
- Procurement recommendation engine with action categorization
- Purchase order management system
- Wildberries and Ozon API client implementations
- Celery-based scheduled synchronization workflow
- Basic procurement dashboard with action-based views

### Critical Gaps for MVP

The following essential MVP components are missing or incomplete:

1. User onboarding wizard and initial setup flow
2. Warehouse management functionality
3. Company settings management (currency, timezone, thresholds)
4. Product catalog import via CSV/XLSX
5. Website/e-commerce platform integration
6. Unified inventory table with multi-warehouse support
7. Inventory movement history tracking
8. Manual stock adjustment capabilities
9. Simplified forecasting based on moving averages
10. Telegram notification system
11. Export functionality for procurement orders
12. Enhanced dashboard with inventory metrics

## Strategic Design Approach

The enhancement strategy follows a modular, incremental approach:

- Prioritize user experience and workflow simplification
- Build upon existing data models without disruptive restructuring
- Maintain consistency with current Django/Celery architecture
- Ensure all features integrate seamlessly with existing procurement dashboard
- Focus on rapid time-to-value for end users

## Feature Specifications

### 1. Onboarding Wizard System

#### Purpose
Guide new users through initial system setup in a structured, progressive manner to achieve first value within minutes.

#### User Flow

The onboarding process consists of sequential steps with progress tracking:

**Step 1: Company Profile Setup**
- Capture company name and basic information
- Set default currency from predefined list (USD, EUR, RUB, etc.)
- Configure timezone for accurate scheduling
- Define low stock threshold in days (default: 7 days)

**Step 2: Warehouse Configuration**
- Create primary warehouse (user's own warehouse)
- Add marketplace fulfillment warehouses (e.g., Ozon Fulfillment)
- Each warehouse requires: name, type (OWN/MARKETPLACE_FF), and associated marketplace if applicable

**Step 3: Marketplace Integration**
- Configure Ozon Seller API credentials (Client-ID and API-Key)
- Configure optional website integration (API endpoint or webhook URL)
- Test connection for each integration
- Display connection status indicators

**Step 4: Product Catalog Import**
- Option A: Manual product entry form (SKU, name, cost, price)
- Option B: CSV/XLSX file upload with column mapping interface
- Preview imported data before confirmation
- Bulk import validation and error reporting

**Step 5: Completion and First Dashboard**
- Trigger initial synchronization job
- Display progress indicator during data loading
- Redirect to main dashboard when ready
- Show success confirmation with next steps

#### Data Model Extensions

Extend Company model settings JSON field to include:

- currency (string)
- timezone (string)
- low_stock_threshold_days (integer)
- onboarding_completed (boolean)
- onboarding_step (integer)

Introduce Warehouse entity:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company | Foreign Key | Reference to Company |
| name | String | Warehouse name |
| warehouse_type | Choice | OWN, MARKETPLACE_FF |
| marketplace | Choice | OZON, WILDBERRIES, WEBSITE, null |
| is_primary | Boolean | Designates default warehouse |
| metadata | JSON | Additional warehouse-specific settings |
| is_active | Boolean | Operational status |
| created_at | DateTime | Record creation timestamp |

#### UI Requirements

- Progress bar showing completion percentage
- Step navigation (back/next buttons)
- Field validation with inline error messages
- Ability to save draft and resume later
- Skip option for non-critical steps
- Responsive layout for mobile and desktop

---

### 2. Enhanced Product Catalog Management

#### Purpose
Enable efficient product data management through both manual entry and bulk import mechanisms.

#### CSV/XLSX Import Functionality

**Import Process Flow**

1. User uploads file through web interface
2. System detects file format and extracts columns
3. User maps CSV columns to system fields via dropdown selectors
4. System displays preview of first 10 rows with mapped data
5. User confirms import or adjusts mappings
6. Background job processes full import with progress tracking
7. System generates import report showing success/failure counts

**Required Column Mappings**

| System Field | Required | Data Type | Validation Rules |
|--------------|----------|-----------|------------------|
| SKU | Yes | String | Unique per company, max 100 chars |
| Product Name | Yes | String | Max 500 chars |
| Cost Price | No | Decimal | Positive number, 2 decimal places |
| Selling Price | No | Decimal | Positive number, 2 decimal places |
| Category | No | String | Max 200 chars |
| Initial Stock | No | Integer | Non-negative integer |
| Warehouse | No | String | Must match existing warehouse name |

**Error Handling Strategy**

- Skip invalid rows and continue processing valid ones
- Generate detailed error report with row numbers and reasons
- Provide downloadable error log in CSV format
- Offer option to re-upload corrected file

#### Manual Product Management

- CRUD interface for individual product creation/editing
- Form validation matching import rules
- Ability to set extended attributes (weight, dimensions, lead times)
- Support for product activation/deactivation without deletion

---

### 3. Warehouse-Aware Inventory Management

#### Purpose
Track inventory across multiple warehouses and provide unified visibility with color-coded stock alerts.

#### Unified Inventory Table

**Table Structure and Columns**

| Column | Data Source | Display Logic |
|--------|-------------|---------------|
| Product | Product.name + SKU | Clickable link to detail view |
| Own Warehouse Stock | InventorySnapshot filtered by primary warehouse | Current quantity |
| Ozon FF Stock | InventorySnapshot filtered by Ozon warehouse | Current quantity, "-" if not mapped |
| Website Stock | InventorySnapshot filtered by website warehouse | Current quantity, "-" if not mapped |
| Total Stock | Sum across all warehouses | Bold text |
| Forecast Depletion | Calculated field | Days until stockout at current burn rate |
| Recommended Order | ProcurementRecommendation.recommended_quantity | Quantity in units |
| Status Indicator | Based on runway days | Color-coded visual badge |

**Color-Coded Status Logic**

| Status | Condition | Visual Indicator |
|--------|-----------|------------------|
| Green (Healthy) | Runway days greater than low_stock_threshold | Green badge, normal text |
| Yellow (Warning) | Runway days between 50% and 100% of threshold | Yellow badge, attention icon |
| Red (Critical) | Runway days less than 50% of threshold | Red badge, urgent icon, bold text |

**Filtering and Sorting Capabilities**

- Filter by status (All, Green, Yellow, Red)
- Filter by warehouse
- Filter by category
- Search by SKU or product name
- Sort by any column (stock level, depletion date, recommended order)
- Pagination with configurable page size

#### Manual Stock Adjustment Interface

**Adjustment Form Fields**

| Field | Type | Purpose |
|-------|------|---------|
| Product | Select | Choose product to adjust |
| Warehouse | Select | Specify which warehouse |
| Adjustment Type | Choice | ADD, SUBTRACT, SET_TO |
| Quantity | Integer | Amount to adjust |
| Reason | Choice | RECEIVING, DAMAGE, LOSS, INVENTORY_COUNT, CORRECTION, OTHER |
| Notes | Text | Optional detailed explanation |
| Adjustment Date | Date | When adjustment occurred (defaults to today) |

**Adjustment Processing Logic**

When user submits adjustment:
1. Validate quantity against business rules (no negative results for SUBTRACT)
2. Create InventoryMovement record with all adjustment details
3. Update or create InventorySnapshot for specified warehouse and date
4. Recalculate affected ProcurementRecommendation if adjustment impacts today's data
5. Update forecast depletion dates for affected product
6. Log action in audit trail

**Business Rules**

- SUBTRACT operations cannot result in negative inventory
- SET_TO operations must use non-negative values
- Adjustments require mandatory reason selection
- Adjustments older than 30 days require additional confirmation
- Large adjustments (greater than 50% of current stock) trigger warning dialog

---

### 4. Inventory Movement History

#### Purpose
Provide complete traceability of inventory changes for auditing, reconciliation, and error investigation.

#### Movement Types

The system tracks six distinct movement categories:

| Type | Trigger | Impact on Inventory |
|------|---------|---------------------|
| INBOUND | Sales sync, purchase order receipt | Increases stock |
| OUTBOUND | Sales sync | Decreases stock |
| TRANSFER | Manual inter-warehouse movement | Neutral (decreases source, increases destination) |
| ADJUSTMENT | Manual correction | Increases or decreases based on type |
| SYNC_UPDATE | Marketplace data synchronization | Updates to match external system |
| INITIAL_LOAD | First-time inventory import | Sets baseline stock |

#### Movement Record Structure

| Field | Description | Source |
|-------|-------------|--------|
| Movement ID | Unique identifier | Auto-generated UUID |
| Product | Product reference | User selection or sync process |
| Warehouse | Warehouse reference | Context-dependent |
| Movement Type | Category of movement | System or user selection |
| Quantity | Signed integer (negative for outbound) | Calculation or user input |
| Movement Date | When movement occurred | Timestamp |
| Reference Type | Source of movement | SALE, PURCHASE_ORDER, ADJUSTMENT, SYNC |
| Reference ID | ID of related record | Foreign key to source entity |
| Notes | Human-readable description | Auto-generated or user-entered |
| Created By | User who initiated | Current user or system |

#### Movement History View

**Display Format**

- Reverse chronological list (newest first)
- Filterable by product, warehouse, date range, movement type
- Searchable by notes content
- Exportable to CSV for external analysis
- Grouped by day with daily summaries

**Per-Movement Display**

- Visual icon indicating movement type
- Product name and SKU
- Warehouse name
- Quantity with directional indicator (+ or -)
- Formatted timestamp
- Clickable reference to source record (if applicable)
- Expandable notes section

---

### 5. Website Integration Module

#### Purpose
Enable synchronization with e-commerce platforms and custom websites to aggregate sales and inventory data from non-marketplace channels.

#### Integration Architecture

**Supported Integration Methods**

| Method | Use Case | Implementation Complexity |
|--------|----------|--------------------------|
| API Client | Direct API connection to platform | Medium - requires platform-specific adapter |
| Webhook Receiver | Platform pushes events to system | Low - standardized webhook handler |
| Manual Upload | CSV file upload for sales/inventory | Very Low - reuses import infrastructure |

#### Generic Website Client

**Client Interface Definition**

The WebsiteClient follows the same abstraction pattern as marketplace clients:

**Required Methods:**
- authenticate: Validates API credentials or tokens
- fetch_sales: Retrieves sales transactions for date range
- fetch_inventory: Retrieves current stock levels
- update_inventory: Pushes stock updates to website (optional)

**Configuration Parameters:**

| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| platform_type | Identifies website platform | WOOCOMMERCE, SHOPIFY, TILDA, CUSTOM_API |
| api_endpoint | Base URL for API | https://mystore.com/api |
| authentication_method | How to authenticate | API_KEY, OAUTH, BASIC_AUTH |
| credentials | Platform-specific auth data | JSON object with keys/tokens |

#### Webhook Handler

**Webhook Event Processing**

Incoming webhook events follow standardized structure:

**Event Types:**
- order.created: New sale transaction
- order.cancelled: Sale reversal
- inventory.updated: Stock level change

**Event Payload Schema:**

Expected fields in webhook JSON:
- event_type: String identifying event category
- timestamp: ISO 8601 datetime
- data: Nested object with event-specific fields

**Sale Event Data Fields:**
- order_id: External order reference
- order_date: When sale occurred
- items: Array of line items with SKU, quantity, price

**Processing Logic:**

1. Validate webhook signature (if platform supports)
2. Parse JSON payload and extract event_type
3. Route to appropriate handler based on event_type
4. Transform platform-specific data to internal format
5. Create or update corresponding internal records
6. Return success/error response to platform

#### Manual Data Upload

**Upload Process:**

Reuse CSV import infrastructure with website-specific templates:

**Sales Upload Template:**
- Order Date (required)
- SKU (required)
- Quantity Sold (required)
- Revenue (optional)
- Order Reference (optional)

**Inventory Upload Template:**
- SKU (required)
- Current Stock (required)
- Last Updated (optional)

---

### 6. Simplified Forecasting Engine

#### Purpose
Provide fast, interpretable demand forecasts for the 14-day horizon using simple statistical methods suitable for MVP validation.

#### Forecasting Methodology

**Moving Average Approach**

For each product, calculate two complementary metrics:

**7-Day Moving Average:**
- Sum sales quantities from last 7 days
- Divide by 7 to get average daily sales
- Use for short-term, responsive forecasting

**14-Day Moving Average:**
- Sum sales quantities from last 14 days  
- Divide by 14 to get average daily sales
- Use for smoothing and trend detection

**Forecast Calculation:**

Daily forecast for next 14 days = Weighted average of both moving averages

Weighting formula:
- If recent trend is stable: 60% weight to 7-day, 40% to 14-day
- If recent volatility is high: 40% weight to 7-day, 60% to 14-day

Volatility detection: Compare standard deviation of last 7 days to last 14 days

**Handling Edge Cases:**

| Scenario | Logic |
|----------|-------|
| Less than 7 days of history | Use simple average of available days |
| Zero sales in period | Forecast 0, flag as "inactive" |
| Negative trend | Use minimum of averages, prevent negative forecasts |
| New product | Require manual seed forecast or use category average |

#### Forecast Data Structure

| Field | Description |
|-------|-------------|
| Product Reference | Link to product being forecasted |
| Forecast Date | Specific future date |
| Predicted Quantity | Calculated expected sales |
| Calculation Method | MOVING_AVERAGE, MANUAL, CATEGORY_DEFAULT |
| Confidence Level | HIGH, MEDIUM, LOW based on data sufficiency |
| Generated At | When forecast was created |
| Data Points Used | Count of historical days included |

#### Depletion Calculation

**Days to Depletion Formula:**

```
Current Total Stock / Average Daily Forecast = Runway Days
```

**Depletion Date:**

```
Today + Runway Days = Estimated Stockout Date
```

**Confidence Indicators:**

- High confidence: Greater than 30 days of sales history, low volatility
- Medium confidence: 14-30 days of history or moderate volatility  
- Low confidence: Less than 14 days or high volatility or new product

---

### 7. Procurement Recommendation Engine

#### Purpose
Calculate actionable order recommendations by combining forecast demand with current inventory and delivery lead times.

#### Recommendation Formula

**Recommended Order Quantity:**

```
(14-Day Forecast Total) + (Lead Time Days × Daily Forecast) + (Safety Stock Days × Daily Forecast) - Current Total Stock - In-Transit Quantity
```

**Components Explained:**

| Component | Calculation | Purpose |
|-----------|-------------|---------|
| 14-Day Forecast Total | Sum of daily forecasts for next 14 days | Cover immediate demand horizon |
| Lead Time Buffer | Lead time days × daily forecast | Cover period from order to delivery |
| Safety Stock Buffer | Safety stock days × daily forecast | Risk mitigation cushion |
| Current Stock Offset | Sum of all warehouse inventory | Account for available inventory |
| In-Transit Offset | Sum of unreceived purchase order quantities | Prevent double-ordering |

**Safety Stock Logic:**

Safety stock days sourced from:
1. Product-specific safety_stock_days in ProductAttributes (if set)
2. Company default from settings (if configured)
3. System default: 3 days

#### Action Category Assignment

Products are categorized based on urgency scoring:

| Category | Criteria | Intended User Action |
|----------|----------|---------------------|
| ORDER_TODAY | Runway days ≤ Lead time days + Safety days | Place order immediately |
| ALREADY_ORDERED | Active PO exists covering forecast period | Monitor delivery, no action |
| ATTENTION_REQUIRED | Runway days ≤ Threshold but other issues present | Investigate and decide |
| NORMAL | Runway days greater than comfortable threshold | No action needed |

**ATTENTION_REQUIRED Triggers:**

- Negative recommended quantity (oversupplied)
- Very high recommended quantity (greater than 3 months forecast)
- Low forecast confidence
- Recent stockout occurred
- Supplier delivery delays noted in system

#### Priority Scoring

Priority score (0-100) determines display order:

**Score Formula:**

```
Base Score = 100 × (1 - (Runway Days / (Lead Time + Safety Stock + 14)))
Adjustments:
- Add 20 if past stockout in last 30 days
- Add 10 if high-value product (cost × forecast greater than threshold)
- Add 10 if forecast confidence is high
- Subtract 20 if recommended quantity is negative
```

Clamped to 0-100 range after adjustments.

---

### 8. Telegram Notification System

#### Purpose
Deliver proactive alerts about critical stock situations to users via Telegram bot, enabling rapid response without requiring dashboard login.

#### Notification Architecture

**Telegram Bot Setup Requirements:**

- Company-level bot token configuration (obtained from BotFather)
- User-level chat ID registration (users send /start to bot)
- Mapping table linking User records to Telegram chat IDs

**Bot Interaction Flow:**

1. User creates bot via BotFather, obtains token
2. User enters token in company settings
3. Users individually message bot with /start command
4. Bot receives message, extracts chat ID
5. System associates chat ID with user account
6. Confirmation sent to user via Telegram

#### Notification Triggers

**Critical Stock Alert:**

Triggered when:
- Product enters RED status (runway ≤ 50% of threshold)
- Product transitions from YELLOW to RED
- Product is in ORDER_TODAY category for first time today

Alert content:
- Product name and SKU
- Current total stock
- Days until stockout
- Recommended order quantity
- Direct link to product detail page or inventory table

**Daily Summary Digest:**

Sent at configurable time (default: 8:00 AM company timezone)

Digest content:
- Count of products in each status category
- List of top 5 most urgent products (highest priority score)
- Link to full dashboard
- Yesterday's sync status summary

**Weekly Report:**

Sent once weekly (default: Monday 9:00 AM)

Report content:
- Total products managed
- Inventory turnover rate (if calculable)
- Top selling products last 7 days
- Low performers (slow moving inventory)
- Forecast accuracy metrics

#### Message Formatting

**Text Message Structure:**

Use Telegram markdown for formatting:
- Bold for critical metrics
- Emojis for visual status indicators (🔴🟡🟢)
- Inline links to deep-link into web dashboard
- Structured layout with sections

**Example Critical Alert:**

```
🔴 CRITICAL STOCK ALERT

Product: Winter Jacket Blue XL
SKU: WJ-BLUE-XL

Current Stock: 12 units
Days to Stockout: 3 days
Recommended Order: 85 units

Action: Order immediately to avoid stockout

[View Product Details] [Go to Dashboard]
```

#### User Preferences

Allow users to configure notification preferences:

| Preference | Options | Default |
|------------|---------|---------|
| Critical Alerts | ON/OFF | ON |
| Daily Digest | ON/OFF | ON |
| Weekly Report | ON/OFF | ON |
| Digest Time | Time selection | 08:00 |
| Alert Threshold | Custom runway days | Company default |

---

### 9. Order Export Functionality

#### Purpose
Generate formatted procurement documents ready for submission to suppliers via email or portal upload.

#### Export Formats

**Excel (XLSX) Format:**

Sheet structure:
- Header row with company name, order date, generation timestamp
- Column headers: SKU, Product Name, Current Stock, Recommended Quantity, Notes
- Data rows for all products with recommended_quantity greater than 0
- Footer row with total SKU count and total units

Formatting:
- Header in bold with company branding color
- Color-coded rows based on priority (red for urgent)
- Frozen header row
- Auto-sized columns
- Borders around cells

**PDF Format:**

Document structure:
- Company header with logo (if configured)
- Order metadata: Order ID, Date, Prepared By
- Table of products matching Excel structure
- Page numbers and generation timestamp in footer
- Professional layout suitable for printing

**CSV Format:**

Simple comma-separated values:
- No special formatting
- Standard column headers
- Suitable for import into supplier systems
- UTF-8 encoding with BOM for international characters

#### Export Workflow

**User Interaction:**

1. User navigates to inventory table or procurement dashboard
2. User applies filters to select specific products (optional)
3. User clicks "Export Order" button
4. Modal dialog appears with export options
5. User selects format (Excel/PDF/CSV)
6. User optionally adds order notes or supplier information
7. System generates file asynchronously
8. Download link appears when ready or file auto-downloads

**Generated File Naming:**

Pattern: `procurement_order_{company_name}_{YYYY-MM-DD}.{extension}`

Example: `procurement_order_MyCompany_2024-01-15.xlsx`

#### Order Tracking Integration

**Optional Enhancement:**

When export is generated:
- Option to create draft Purchase Order in system
- Pre-populate PO with exported items
- Track which exports were converted to actual orders
- Link back from PO to export record

---

### 10. Enhanced Dashboard

#### Purpose
Provide at-a-glance visibility into inventory health and business metrics through visual summary widgets.

#### Dashboard Widgets

**1. Total Inventory Value**

Display:
- Sum of (quantity × cost_price) across all products and warehouses
- Formatted as currency in company's configured currency
- Comparison indicator showing change from previous period (e.g., "↑ 5.2% vs last week")

**2. Average Inventory Turnover**

Calculation:
- For each product: (Last 30 days sales) / (Average stock over period)
- Weighted average across all products
- Displayed in days (e.g., "Average turnover: 22 days")

Interpretation:
- Lower is generally better (faster inventory movement)
- Color coding: Green if less than 30 days, Yellow 30-60 days, Red greater than 60 days

**3. Stock Status Distribution**

Visualization:
- Donut chart or stacked bar showing proportion of products in each status
- Segments: Green (healthy), Yellow (warning), Red (critical)
- Percentage labels on each segment
- Clickable segments filter inventory table to that status

**4. Top Urgent Products**

List display:
- Top 5 products with highest priority score
- For each: Product name, SKU, runway days, recommended order
- Visual urgency indicator
- Click to navigate to product detail

**5. Recent Activity Summary**

Timeline of recent events:
- Last synchronization time and status
- Recent manual adjustments count
- Recent purchase orders created
- Forecast generation timestamp

**6. Forecast Accuracy Tracker**

If sufficient history exists:
- Display average forecast error percentage
- Trend indicator (improving/declining)
- Link to detailed accuracy report

#### Dashboard Layout

**Responsive Grid Structure:**

Desktop (greater than 1024px):
- 3-column grid
- Widgets occupy 1-2 column spans based on content density
- Full inventory table below widgets

Tablet (768px - 1024px):
- 2-column grid
- Some widgets stack vertically

Mobile (less than 768px):
- Single column
- Widgets prioritized by importance
- Collapsible sections

---

## Technical Integration Strategy

### Database Schema Enhancements

**New Tables Required:**

1. Warehouse
   - Extends multi-warehouse support
   - Foreign key to Company
   - Indexes on company_id, warehouse_type

2. InventoryMovement
   - Tracks all inventory changes
   - Foreign keys to Product, Warehouse, User
   - Indexes on movement_date, product_id, warehouse_id

3. TelegramSubscription
   - Maps users to Telegram chat IDs
   - Foreign key to User
   - Unique constraint on chat_id

4. OnboardingState
   - Tracks onboarding progress
   - Foreign key to Company
   - Stores step-specific data in JSON

**Modified Tables:**

1. Company model settings field additions
2. InventorySnapshot add warehouse_id foreign key (currently stores warehouse_id as string)
3. MarketplaceCredential add support for WEBSITE marketplace type

### API Endpoints

**Onboarding API:**

- POST /api/onboarding/company - Create company profile
- POST /api/onboarding/warehouse - Add warehouse
- POST /api/onboarding/integration - Configure integration
- POST /api/onboarding/products/import - Bulk import products
- GET /api/onboarding/status - Get current onboarding state

**Inventory Management API:**

- GET /api/inventory - List inventory with filters
- POST /api/inventory/adjust - Submit manual adjustment
- GET /api/inventory/movements - Retrieve movement history
- GET /api/inventory/movements/:product_id - Product-specific movements

**Integration API:**

- POST /api/integrations/webhook - Receive external webhooks
- POST /api/integrations/test - Test integration connection
- GET /api/integrations/status - Get sync status

**Export API:**

- POST /api/export/order - Generate procurement export
- GET /api/export/order/:export_id - Download generated file

**Dashboard API:**

- GET /api/dashboard/metrics - Retrieve dashboard widget data
- GET /api/dashboard/urgent-products - Get top urgent items

**Telegram API:**

- POST /api/telegram/register - Register chat ID
- POST /api/telegram/preferences - Update notification settings
- POST /api/telegram/webhook - Receive bot messages

### Background Job Extensions

**New Celery Tasks:**

1. `process_product_import(file_id, company_id, column_mapping)`
   - Processes uploaded CSV/XLSX files
   - Creates Product and initial InventorySnapshot records
   - Generates import report

2. `send_telegram_notification(user_id, message_type, data)`
   - Sends individual Telegram messages
   - Retries on failure
   - Logs delivery status

3. `generate_daily_digest(company_id)`
   - Compiles daily summary data
   - Sends to all subscribed users
   - Scheduled via Celery Beat

4. `generate_procurement_export(export_id, format, filters)`
   - Creates formatted export files
   - Stores in temporary file storage
   - Triggers download notification

5. `calculate_simple_forecasts(company_id)`
   - Runs moving average calculations
   - Updates Forecast records
   - Replaces existing ML-heavy forecasting for MVP

6. `sync_website_data(credential_id)`
   - Fetches data from website integrations
   - Processes webhook queue
   - Updates sales and inventory

**Modified Tasks:**

1. `analyze_all_procurement`
   - Enhance to use simplified forecasts
   - Calculate warehouse-aware recommendations
   - Generate Telegram alerts for critical items

2. `sync_marketplace`
   - Support WEBSITE marketplace type
   - Update warehouse-specific inventory snapshots

### Frontend Components

**Onboarding Wizard:**
- Multi-step form component with progress tracking
- File upload widget with drag-and-drop
- Connection test indicators
- Validation error display

**Inventory Table:**
- Sortable, filterable data table
- Color-coded status badges
- Inline quick actions (adjust stock)
- Responsive mobile view

**Stock Adjustment Modal:**
- Form with dependent dropdown fields
- Real-time quantity preview
- Confirmation step for large changes

**Movement History:**
- Infinite scroll or paginated list
- Date range picker
- Filter chips
- Export button

**Dashboard Widgets:**
- Metric card components
- Chart visualizations (using Chart.js or similar)
- Responsive grid layout

---

## Data Migration Strategy

### Migration for Existing Data

**Warehouse Backfill:**

For existing companies without warehouse records:
1. Create default "Main Warehouse" with type OWN and is_primary=true
2. Create marketplace warehouses for each active MarketplaceCredential
3. Associate existing InventorySnapshot records with appropriate warehouse

**Movement History Generation:**

For historical inventory data:
1. Analyze existing SalesTransaction records
2. Generate OUTBOUND movements for each sale
3. Mark movements as auto-generated with reference to original transaction
4. Do not generate movements for data older than 90 days to limit volume

**Forecast Data Transition:**

1. Preserve existing ML-based forecasts in database
2. Run initial simple forecast calculation
3. Compare results and flag significant deviations
4. Gradually phase out ML forecasts as simple forecasts prove sufficient

### Data Validation Rules

**Pre-MVP Launch Checks:**

- All companies have at least one warehouse
- All active products have inventory snapshot for today
- All users have valid email addresses
- All marketplace credentials tested and validated
- All forecast records have generated_at timestamps

---

## User Experience Guidelines

### Progressive Disclosure

- Show basic features first, advanced options behind "More" or "Advanced"
- Onboarding reveals complexity gradually step by step
- Dashboard defaults to simplified view with option to expand

### Error Handling Principles

- Validation errors appear inline with specific guidance
- System errors show user-friendly messages with support contact
- Failed background jobs notify user with retry option
- Import errors provide downloadable error report

### Performance Targets

- Inventory table loads in under 2 seconds for up to 1000 products
- Dashboard metrics render in under 1 second
- CSV import of 500 products completes in under 30 seconds
- Telegram notifications deliver within 5 seconds of trigger

### Accessibility Considerations

- Color-coded statuses also use icons for color-blind users
- Keyboard navigation support for all interactive elements
- ARIA labels for screen readers
- Responsive design for mobile accessibility

---

## Security and Privacy

### Data Protection

- Warehouse data visible only to users within same company
- API credentials encrypted at rest in database
- Telegram chat IDs stored securely and not exposed in logs
- Export files auto-deleted after 24 hours

### Authentication and Authorization

- Onboarding wizard requires authenticated user
- Inventory adjustments log user who made change
- Export functionality requires appropriate role permissions
- Telegram bot validates chat ID before sending messages

### Input Validation

- CSV uploads scanned for malicious content
- File size limits enforced (maximum 10MB for imports)
- API webhook signatures validated when platform supports
- SQL injection prevention via parameterized queries

---

## Testing Strategy

### Unit Testing Focus Areas

- Moving average forecast calculation accuracy
- Recommendation quantity formula correctness
- Status category assignment logic
- CSV parsing and validation
- Webhook payload parsing

### Integration Testing Scenarios

- End-to-end onboarding flow completion
- Product import with various file formats
- Manual stock adjustment triggering recommendation update
- Telegram notification delivery after status change
- Export generation and file download

### User Acceptance Testing

- Complete onboarding as new user within 10 minutes
- Import 50 products via CSV and verify accuracy
- Manually adjust stock and confirm movement recorded
- Receive Telegram alert for critical stock
- Generate and download procurement order export

---

## Deployment Considerations

### Phased Rollout Plan

**Phase 1: Foundation (Week 1-2)**
- Deploy warehouse management
- Implement CSV import
- Launch simplified forecasting

**Phase 2: User Interface (Week 3-4)**
- Release onboarding wizard
- Deploy enhanced inventory table
- Add manual adjustment interface

**Phase 3: Integrations (Week 5-6)**
- Enable website integration
- Launch Telegram notifications
- Implement export functionality

**Phase 4: Polish (Week 7-8)**
- Complete dashboard enhancements
- Performance optimization
- Bug fixes and UX refinements

### Infrastructure Requirements

**No Additional Services:**
- Reuses existing PostgreSQL, Redis, Celery infrastructure
- Telegram integration uses webhook mode (no polling)
- File storage uses local filesystem or existing S3 bucket

**Configuration Changes:**
- Add Telegram Bot API credentials to environment variables
- Configure file upload directory and size limits
- Set Celery worker concurrency for import tasks

### Monitoring and Observability

**Key Metrics to Track:**

- Onboarding completion rate
- Average time to complete onboarding
- Product import success rate
- Telegram notification delivery rate
- Export generation frequency
- User engagement with inventory table

**Alerts to Configure:**

- Telegram notification failures
- CSV import job failures
- Webhook processing errors
- Forecast calculation failures

---

## Success Criteria

The MVP enhancement is considered complete when:

1. New users can complete onboarding and see their first dashboard within 15 minutes
2. Users can import product catalog via CSV with greater than 95% success rate
3. Inventory table displays multi-warehouse stock with color-coded alerts
4. Manual stock adjustments reflect immediately in inventory and forecasts
5. Simplified forecasting generates 14-day predictions for all active products daily
6. Procurement recommendations calculate correct order quantities
7. Telegram notifications deliver within 5 seconds for critical alerts
8. Users can export procurement orders in Excel, PDF, and CSV formats
9. Dashboard displays accurate inventory metrics and top urgent products
10. System handles 100 concurrent users and 1000+ products per company without performance degradation

---

## Future Enhancements Beyond MVP

The following features are intentionally deferred to post-MVP iterations:

- Advanced ML forecasting reintroduction with A/B testing against simple forecasts
- Supplier management module with lead time tracking
- Automated purchase order generation
- Multi-currency support for international operations
- Advanced analytics and reporting dashboard
- Mobile native applications
- Integration marketplace with pre-built connectors
- AI-powered anomaly detection in inventory patterns
- Collaborative features for team workflows
- Custom alert rules and conditions
