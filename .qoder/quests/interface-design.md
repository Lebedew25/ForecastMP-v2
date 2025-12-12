# Frontend Interface Design - ForecastMP-v2

## 1. Technology Stack Selection

### 1.1 Core Framework & Language

**Selected Stack: React + TypeScript**

Rationale for technology selection:

- **React Framework**: Component-based architecture enables creation of reusable UI elements such as product cards, table rows, and dashboard widgets. Rich ecosystem with extensive community support and high performance for dynamic data-heavy interfaces.

- **TypeScript**: Essential for managing complex structured data domains including products, warehouses, orders, and transactions. Provides compile-time type checking to reduce runtime errors and improves collaboration between frontend and Django backend through shared type contracts.

### 1.2 UI Component Library

**Selected: Ant Design for React**

Strategic advantages:

- Provides production-ready data-dense components including advanced tables with sorting, filtering, and pagination capabilities
- Professional design system optimized for enterprise applications
- Built-in components for complex forms, modal dialogs, and multi-step wizards
- Accelerates development timeline by 3-5x compared to custom component development
- Consistent with target aesthetic of modern data-driven design

### 1.3 Supporting Libraries

| Category | Library | Purpose |
|----------|---------|---------|
| Charts & Visualization | Recharts | Lightweight, customizable charting library for dashboard metrics and trend visualization |
| State Management | Redux Toolkit | Centralized state management for user data, product listings, and application settings |
| Routing | React Router v6 | Single Page Application navigation without page reloads |
| HTTP Client | Axios | Structured API communication with Django backend endpoints |
| Form Handling | React Hook Form | Efficient form validation and submission handling |
| Date Manipulation | Day.js | Lightweight date formatting and manipulation |

## 2. Design System Specification

### 2.1 Target Audience Profile

**Primary Users**: Russian small-to-medium e-commerce business owners and operational staff

**User Characteristics**:
- Time-constrained professionals requiring quick decision-making capabilities
- Value clarity, practicality, and actionable insights over aesthetic complexity
- Need to manage multiple sales channels and inventory locations simultaneously

### 2.2 Visual Design Philosophy

**Design Approach: Modern Data-Driven Design with Neo-Skeuomorphic Elements**

Core principles:
- Clean, spacious interfaces with generous white space for reduced cognitive load
- Card-based layouts with subtle shadows for visual grouping and hierarchy
- Clear visual hierarchy emphasizing the most critical information and actions
- Data density balanced with readability

### 2.3 Color Palette

**Primary Color Scheme**:

| Color Function | Hex Code | Usage Context |
|----------------|----------|---------------|
| Primary/Accent | #1890FF | Primary action buttons, active links, key indicators |
| Background Base | #FFFFFF | Main page backgrounds |
| Background Secondary | #F5F5F5 | Section dividers, card backgrounds |
| Success/Adequate Stock | #52C41A | Sufficient inventory, active products |
| Danger/Critical Stock | #F5222D | Low stock alerts, requires immediate action |
| Warning/Low Stock | #FA8C16 | Stock running low, reorder soon |
| Neutral/Disabled | #BFBFBF | Inactive elements, disabled states |

**Status Badge Colors**:
- Green badges: Inventory runway exceeds 30 days
- Orange badges: Inventory runway 7-30 days
- Red badges: Inventory runway less than 7 days
- Gray badges: Inactive or no data

### 2.4 Typography System

**Font Family**: Inter or SF Pro Display

**Type Scale**:

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| Page Title | 24px | Semi-Bold | Main page headings |
| Section Header | 16px | Semi-Bold | Subsection titles, table headers |
| Body Text | 14px | Regular | Primary content, table cells |
| Supporting Text | 12px | Regular | Metadata, timestamps, helper text |

### 2.5 Interface Design Principles

**Principle 1: Forecast Visibility**
- Every product listing displays a colored forecast badge indicating days until stockout
- Visual indicators use consistent color semantics across all screens

**Principle 2: Single Source of Truth**
- Any product reference is clickable, opening a detailed modal with complete history and analytics
- Consistent product card layout across all contexts

**Principle 3: Contextual Actions**
- Action buttons appear adjacent to relevant data based on context
- Example: "Write-off", "Order", "Discount" buttons appear in low-stock reports

**Principle 4: Progressive Disclosure**
- Dashboard shows only key metrics at top level
- Detailed analysis and complex reports accessible within 1-2 clicks
- Drill-down navigation from summary to detail views

## 3. Application Navigation Structure

### 3.1 Main Navigation Layout

**Navigation Pattern**: Persistent vertical sidebar (left-aligned)

**Sidebar Components**:
- Top: Application logo and branding
- Middle: Primary navigation menu
- Bottom: User avatar, settings, and account controls

**Navigation Menu Items**:

```
Dashboard
├─ Icon: Line chart/analytics

Products
├─ Icon: Package/box
├─ All Products
├─ Categories
└─ Import/Export

Inventory
├─ Icon: Warehouse
├─ Overview Table
├─ By Warehouse
├─ Stock Adjustments
└─ Movement History

Forecasting & Orders (Phase 2.0)
├─ Icon: Growth curve
└─ [Future implementation]

Reports (Phase 2.0)
├─ Icon: Document
└─ [Future implementation]

Settings
├─ Icon: Gear
├─ Company Profile
├─ Warehouses & Locations
├─ Sales Channels (Integrations)
├─ Team Management
└─ Notification Preferences
```

**Navigation Behavior**:
- Active menu item highlighted with accent color
- Submenu items expand on parent selection
- Breadcrumb trail displayed for nested views

### 3.2 Excluded Navigation Contexts

The sidebar navigation is NOT displayed on:
- `wizard.html` - Onboarding wizard flow
- `no_company.html` - Company assignment error state

## 4. Page Specifications

### 4.1 Dashboard Page (dashboard.html)

**Page Objective**: Provide instant business health snapshot focusing on inventory status and critical alerts

#### 4.1.1 Key Performance Indicators Panel

**Layout**: Horizontal card row displaying 4-6 primary metrics

**Metrics**:

| Metric | Description | Data Source |
|--------|-------------|-------------|
| Total Inventory Value | Sum of all stock value in company currency | Product quantity × cost price across all warehouses |
| Average Turnover | Mean inventory turnover rate in days | Rolling 30-day calculation |
| Low Stock Items | Count of products below minimum threshold | Products where current stock < reorder point |
| Dead Stock Items | Products with no movement for 90+ days | Sales history analysis |
| Today's Sales | Revenue generated today | Daily sales aggregate |
| Weekly Sales | Revenue for current week | Weekly sales aggregate |

**Visual Representation**:
- Large numerical value
- Percentage change indicator (up/down arrow with color coding)
- Sparkline showing 7-day trend

#### 4.1.2 Primary Visualization Area

**Chart 1: Inventory & Sales Dynamics (30-day trend)**
- Dual-axis line chart
- Left axis: Total inventory value
- Right axis: Daily sales volume
- Time range: Last 30 days
- Interactive tooltips showing exact values

**Chart 2: Product Performance Distribution**
- Dual-component visualization:
  - Top 5 products by sales velocity (horizontal bar chart, green)
  - Bottom 5 slow-moving products (horizontal bar chart, orange/red)
- Sortable by different metrics (revenue, units, turnover rate)

#### 4.1.3 Attention Required Widget

**Purpose**: Automated priority queue for items requiring immediate action

**Data Source**: Algorithm prioritizing:
1. Negative stock (overselling situations)
2. Forecast depletion within 3 days
3. No stock movement for extended period

**Display Format**: Table with 10-15 rows

**Columns**:
- Product thumbnail image
- SKU and product name
- Issue type badge (colored indicator)
- Current stock level
- Forecast depletion date
- Quick action button (context-dependent)

**Action Buttons**:
- "Order Now" - Opens procurement form pre-filled with product
- "Write Off" - Initiates inventory adjustment workflow
- "Review" - Opens detailed product analysis modal

#### 4.1.4 Recent Activity Feed

**Purpose**: Real-time visibility into inventory operations

**Display**: Vertical timeline showing last 10 operations

**Entry Format**:
- Timestamp (relative: "5 minutes ago", "2 hours ago")
- Operation type icon (color-coded)
- Description: "{Product SKU} - {Operation} - {Quantity} units"
- User responsible for action
- Related warehouse

**Operation Types**:
- Inbound (green icon)
- Outbound/Sale (blue icon)
- Transfer (purple icon)
- Adjustment (orange icon)

### 4.2 All Products Page

**Page Objective**: Comprehensive product catalog with search, filtering, and bulk operations

#### 4.2.1 Control Panel

**Search Functionality**:
- Full-text search across SKU, product name, and category
- Search-as-you-type with debouncing
- Clear search button

**Mass Action Buttons**:
- "Import Products" - Opens import wizard
- "Export to Excel" - Downloads current filtered view
- "Manage Categories" - Category management modal

**Filter Badges** (Toggle filters):
- All Products (default)
- Low Stock (below reorder threshold)
- Out of Stock (zero quantity)
- No Movement (X days, configurable)
- By Category (dropdown selector)

#### 4.2.2 Product Table

**Component**: Ant Design Table with advanced features

**Table Capabilities**:
- Column sorting (ascending/descending)
- Column resizing
- Fixed header on scroll
- Row selection (checkboxes for bulk operations)
- Virtualized scrolling for performance with large datasets

**Column Specification**:

| Column | Width | Content | Sortable |
|--------|-------|---------|----------|
| Thumbnail | 60px | Product image or placeholder | No |
| SKU | 120px | Product SKU identifier | Yes |
| Name | Flex | Product name, truncated with tooltip | Yes |
| Category | 150px | Product category | Yes |
| Total Stock | 100px | Sum across all warehouses | Yes |
| My Warehouse | 100px | Stock at user's primary warehouse | Yes |
| Forecast Depletion | 120px | Colored badge with days remaining | Yes |
| Cost Price | 100px | Per-unit cost | Yes |
| Selling Price | 100px | Current retail price | Yes |
| Actions | 80px | Dropdown menu | No |

**Forecast Depletion Badge Logic**:
- Green: > 30 days
- Orange: 7-30 days
- Red: < 7 days
- Gray: Insufficient data

**Row Interaction**:
- Single click on row: Opens detailed product modal
- Hover: Subtle background color change

**Actions Dropdown Menu**:
- Write Off Inventory
- Reserve Stock
- Adjust Price
- Transfer to Another Warehouse
- View Full History

#### 4.2.3 Product Detail Modal

**Trigger**: Click on any product row

**Modal Structure**: Tabbed interface

**Tab 1: Overview**
- Product images (gallery if multiple)
- Basic attributes (SKU, name, category, description)
- Current stock levels per warehouse (table)
- Pricing information

**Tab 2: Sales History**
- Sales by channel (breakdown table)
- 30/60/90-day sales trend chart
- Seasonal pattern visualization

**Tab 3: Stock Movement**
- Chronological movement log (last 50 transactions)
- Filterable by movement type
- Chart showing stock level changes over time

**Tab 4: Forecast & Orders**
- Current forecast model parameters
- Predicted demand curve
- Linked purchase orders (active and historical)

### 4.3 Inventory by Warehouse Page

**Page Objective**: Warehouse-specific inventory control and cross-location visibility

#### 4.3.1 Warehouse Selector

**Component**: Dropdown selector or horizontal tab navigation

**Display Elements**:
- Warehouse name
- Warehouse type badge (Own, Ozon FF, WB FF)
- Summary metrics below selector:
  - Total SKU count
  - Total inventory value
  - Last sync timestamp (for marketplace warehouses)

**Behavior**:
- Selecting warehouse filters all data on page
- Default: User's primary warehouse

#### 4.3.2 Warehouse Inventory Table

**Table Structure**: Similar to All Products table with warehouse-specific columns

**Modified Columns**:

| Column | Description |
|--------|-------------|
| Product | SKU, name, thumbnail |
| Reserved Quantity | Stock allocated to pending orders |
| Available Quantity | Stock available for sale |
| Expected Inbound | Quantity in incoming purchase orders |
| Stock at Other Locations | Expandable row showing breakdown by warehouse |
| Last Movement | Date and type of last operation |
| Quick Adjust | Inline quantity editor |

**Stock at Other Locations (Expandable)**:
- Click to expand nested table
- Shows quantity at each other warehouse
- Transfer button for inter-warehouse movement

#### 4.3.3 Quick Adjustment Interface

**Purpose**: Rapid stock level corrections without full workflow

**Inline Controls**:
- Current quantity display
- +/- increment buttons
- Direct quantity input field
- Reason dropdown (required):
  - Damaged goods
  - Found stock
  - Counting error
  - Return from customer
  - Other (requires comment)
- Submit button

**Validation**:
- Prevent negative stock unless explicitly permitted
- Confirmation modal for large adjustments (> 20% change)

**Audit Trail**:
- All adjustments logged to InventoryMovement model
- User attribution automatic
- Timestamp and reason captured

### 4.4 Stock Adjustment Workflow Page

**Page Objective**: Formalized multi-step process for structured inventory operations

**Implementation Pattern**: Wizard/Stepper interface (Ant Design Steps component)

#### Step 1: Operation Type Selection

**Radio Group Options**:

| Operation Type | Description | Use Case |
|---------------|-------------|----------|
| Inbound | Increase stock | Receiving purchase orders, returns |
| Outbound | Decrease stock | Waste, damage, internal use |
| Transfer | Move between warehouses | Redistribution, fulfillment preparation |
| Inventory Count | Reconciliation | Physical inventory verification |

**Next Button**: Advances to step 2

#### Step 2: Product & Details Entry

**Interface Elements**:

**Product Selector**:
- Autocomplete search field
- Displays SKU, name, current stock as you type
- Add product button (adds row to table below)

**Adjustment Table**:

| Column | Input Type | Required | Notes |
|--------|------------|----------|-------|
| Product | Read-only | Yes | From selection |
| Warehouse | Dropdown | Yes | Source/destination |
| Quantity | Number input | Yes | Positive integer |
| Unit Cost | Decimal input | Conditional | Required for Inbound |
| Reason | Dropdown | Yes | Predefined list |
| Notes | Text input | No | Additional context |

**For Transfer Operations**:
- Add "Destination Warehouse" column
- Validate source has sufficient stock

**For Inventory Count**:
- Upload CSV option:
  - Format: SKU, Counted Quantity
  - System calculates discrepancies automatically
  - Preview discrepancies before applying

**Bottom Actions**:
- Back button
- Clear All button
- Next button (validates entries)

#### Step 3: Confirmation & Review

**Summary Display**:
- Operation type badge
- Total products affected (count)
- Total quantity change (sum)
- Total value impact (calculated)

**Detailed Review Table**:
- Read-only view of all entries from Step 2
- Color-coded by operation type
- Edit button returns to Step 2

**Commitment Controls**:
- Comment field (optional, for overall operation notes)
- "Confirm & Execute" button (primary action)
- "Cancel" button (returns to inventory page)

#### Step 4: Completion Confirmation

**Success State**:
- Checkmark icon
- "Operation completed successfully" message
- Summary of changes applied
- Link to view movement in history
- "Perform Another Operation" button
- "Return to Dashboard" button

**Error State** (if any item fails):
- Error icon and message
- List of items that succeeded
- List of items that failed with error reasons
- Retry button
- Support contact information

### 4.5 Inventory Movement History Page

**Page Objective**: Comprehensive, auditable log of all stock transactions

#### 4.5.1 Advanced Filter Panel

**Filter Controls** (Collapsible panel):

| Filter | Component Type | Options |
|--------|----------------|---------|
| Date Range | Date range picker | Presets: Today, Last 7 days, Last 30 days, Custom |
| Movement Type | Multi-select dropdown | Inbound, Outbound, Transfer, Adjustment, Sync |
| Warehouse | Multi-select dropdown | All company warehouses |
| Product | Autocomplete search | Search by SKU or name |
| Category | Dropdown | Product categories |
| User | Multi-select dropdown | Team members |
| Minimum Quantity | Number input | Filter movements >= X units |

**Filter Actions**:
- Apply Filters button
- Clear All Filters button
- Save Filter Preset (for frequent searches)

#### 4.5.2 Movement History Table

**Performance Optimization**: Virtual scrolling for large datasets (10,000+ records)

**Column Layout**:

| Column | Width | Content |
|--------|-------|---------|
| Date & Time | 160px | Full timestamp, sortable |
| Type | 120px | Colored badge with icon |
| Product | 200px | SKU + name (truncated) |
| Quantity | 100px | +/- indicator with number |
| Warehouse | 150px | Source (and destination for transfers) |
| Reason | 150px | Predefined reason code |
| User | 120px | Responsible user name |
| Reference | 120px | Link to related document |
| Details | 60px | Expand icon |

**Movement Type Badge Colors**:
- Inbound: Green background
- Outbound: Blue background
- Transfer: Purple background
- Adjustment: Orange background
- Sync: Gray background

**Expandable Row Details**:
- Click to expand additional metadata
- Full notes/comments
- Complete JSON metadata
- Before/after stock levels

**Reference Column Behavior**:
- If linked to sales transaction: Opens sales detail modal
- If linked to purchase order: Opens PO detail modal
- If manual adjustment: Shows adjustment workflow ID

#### 4.5.3 Export Functionality

**Export Button**: Downloads filtered history as CSV

**CSV Format**:
- All visible columns
- ISO 8601 timestamps
- Flattened structure (one row per movement)
- UTF-8 encoding with BOM for Excel compatibility

### 4.6 Company Settings Page

**Page Objective**: Centralized configuration for company-level business logic

**Layout Pattern**: Vertical card stack or horizontal tabs

#### Section 1: Basic Information

**Fields**:

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Company Name | Text input | Yes | 2-100 characters |
| Tax ID (INN) | Text input | Yes | 10 or 12 digits |
| Logo | File upload | No | PNG/JPG, max 2MB |
| Primary Currency | Dropdown | Yes | RUB, USD, EUR |
| Time Zone | Dropdown | Yes | Moscow, Ekaterinburg, etc. |

#### Section 2: Financial Configuration

**Inventory Valuation Method**:
- Radio group: FIFO, Weighted Average
- Helper text explaining each method's impact

**Rounding Rules**:
- Currency rounding: Nearest 0.01, 0.10, 1.00
- Quantity rounding: Always round up/down/nearest

#### Section 3: Inventory Management Rules

**Automatic Reservation**:
- Checkbox: "Reserve stock when order is created"
- Affects stock availability calculations

**Write-off Rules**:
- Approval required for quantities > X
- Designated approvers (multi-select users)

**Stockout Threshold**:
- Number input: Days of inventory runway triggering low-stock alerts
- Applied to forecast depletion badges

#### Section 4: Notification Preferences

**Global Notification Toggles**:

| Notification Type | Channels | Frequency |
|-------------------|----------|-----------|
| Low Stock Alerts | Email, Telegram | Immediate |
| Daily Digest | Email, Telegram | 8:00 AM daily |
| Weekly Summary | Email, Telegram | Monday 9:00 AM |
| Forecast Updates | Email | After forecast run |

**Stock Alert Thresholds**:
- Critical: X days runway
- Warning: Y days runway
- Dead stock: Z days no movement

**Save Button**: Commits all changes with validation

### 4.7 Warehouse Management Page

**Page Objective**: CRUD operations for warehouse entities

#### 4.7.1 Warehouse List View

**Display Format**: Card grid or table layout

**Card Content** (for each warehouse):
- Warehouse name (header)
- Type badge (Own Warehouse, Ozon FF, WB FF, Website)
- Address or location identifier
- Active/Inactive toggle
- SKU count (number of distinct products)
- Total inventory value
- Action buttons: Edit, Deactivate/Activate, Delete

**List Actions**:
- "Add New Warehouse" button (primary action)
- Search/filter by warehouse type

#### 4.7.2 Warehouse Create/Edit Form

**Form Fields**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Warehouse Name | Text input | Yes | Unique per company |
| Warehouse Type | Radio group | Yes | Own, Marketplace Fulfillment |
| Marketplace | Dropdown | Conditional | Required if type = Marketplace FF |
| Address | Text area | No | Physical location |
| Set as Primary | Checkbox | No | Only one primary per company |
| Active Status | Toggle | Yes | Default: Active |

**Virtual Inventory Settings Section** (Critical Feature):

**Purpose**: Control how system calculates "available" stock

**Configuration Options**:

| Setting | Type | Description | Default |
|---------|------|-------------|---------|
| Include Reserved Stock | Checkbox | Count reserved quantities in totals | Unchecked |
| Include Inbound Orders | Checkbox | Count expected shipments in available stock | Unchecked |
| Reserved Stock Offset (days) | Number | Days ahead to consider reservations | 7 |
| Inbound Lead Time (days) | Number | Expected days for inbound to arrive | 14 |

**Notification Settings for Warehouse**:
- Low stock threshold (warehouse-specific override)
- Notification recipients (subset of team)

**Form Actions**:
- Save button
- Cancel button
- Delete Warehouse button (confirmation required)

**Deletion Validation**:
- Cannot delete if warehouse has current stock
- Cannot delete primary warehouse
- Suggest transfer wizard if stock exists

### 4.8 Product Import Page

**Page Objective**: Flexible bulk data ingestion with validation and error handling

**Layout**: Tabbed interface

#### Tab 1: File Import (CSV/XLSX)

**File Upload Area**:
- Drag-and-drop zone
- File browser button
- Accepted formats: .csv, .xlsx, .xls
- Maximum file size: 10 MB
- Download sample template link

**Column Mapping Interface**:

**Workflow**:
1. User uploads file
2. System displays first 5 rows as preview table
3. For each column in file, user maps to system field:

| File Column Header | Maps To (Dropdown) |
|-------------------|-------------------|
| [Auto-detected] | SKU, Name, Category, Cost, Price, Stock, etc. |

**Required Field Validation**:
- SKU (required)
- Name (required)
- At least one of: Cost or Price (warning if missing)

**Import Configuration Options**:

| Option | Type | Default |
|--------|------|---------|
| Create new products | Checkbox | Checked |
| Update existing products | Checkbox | Checked |
| Match products by | Radio | SKU (vs. Name, vs. Both) |
| On row error | Radio | Skip row and continue |
| Import stock levels | Checkbox | Unchecked (requires warehouse selection) |
| Target warehouse | Dropdown | Conditional on above |

**Execute Import Button**:
- Validates data
- Processes in background for large files
- Shows progress bar

**Import Results Log**:

**Display after completion**:
- Total rows processed
- Successful imports (count)
- Failed rows (count)
- Download error report (CSV with error messages per row)

**Error Report Format**:
- Original row number
- Product SKU (if parseable)
- Error type (Missing Required Field, Duplicate SKU, Invalid Format, etc.)
- Error message

#### Tab 2: Marketplace Integrations

**Integration Cards** (One per supported marketplace):

**Card Structure**:

| Element | Description |
|---------|-------------|
| Marketplace Logo | Ozon, Wildberries, Custom Website |
| Connection Status | Badge: Connected (green), Not Connected (gray), Error (red) |
| Last Sync Timestamp | Relative time display |
| Action Buttons | Connect / Configure / Sync Now / Disconnect |

**Connection Flow** (Click "Connect"):
1. Modal opens requesting API credentials
2. Fields specific to marketplace:
   - **Ozon**: Client ID, API Key
   - **Wildberries**: API Token, Supplier ID
   - **Website**: Webhook URL, Secret Key
3. Test Connection button validates credentials
4. Save button stores encrypted credentials

**Configuration Modal**:

**Sync Settings**:
- Auto-sync frequency: Hourly, Daily, Manual only
- Sync scope: Products, Sales, Inventory (checkboxes)
- Field mapping overrides (advanced): Map marketplace fields to custom product attributes

**Manual Sync Button**:
- Triggers immediate sync job
- Progress indicator
- Completion notification with summary:
  - Products synced
  - Sales imported
  - Errors encountered

**Sync History Link**:
- Opens modal with recent sync log
- Table: Timestamp, Status, Records Processed, Errors

### 4.9 Onboarding Wizard (wizard.html)

**Page Objective**: Guided first-time setup for new users

**Access Trigger**: Automatic redirect for users with no associated company

**Wizard Structure**: Multi-step stepper (non-skippable, linear progression)

#### Step 1: Company Creation

**Form Elements**:
- Company Name (text input, required)
- Tax ID (text input, required, validated format)
- Primary Currency (dropdown, required)
- Industry (dropdown, optional, for analytics)

**Visual**: Welcome message, illustration

**Actions**: Next button (validates before proceeding)

#### Step 2: First Warehouse Setup

**Form Elements**:
- Warehouse Name (text input, required, defaults to "Main Warehouse")
- Warehouse Type (radio group, defaults to "Own Warehouse")
- Address (text input, optional)

**Context Message**: "You need at least one warehouse to start tracking inventory"

**Actions**: Back, Next

#### Step 3: Import Initial Products

**Options Presented**:

| Option | Description | Action |
|--------|-------------|--------|
| Upload File | Import from CSV/XLSX | Opens file picker, uses same import logic as main import page |
| Manual Entry | Add products one by one | Opens simple form (SKU, Name, Quantity) with "Add Another" button |
| Skip for Now | Continue without products | Warning: Limited functionality until products added |

**Validation**: At least 1 product recommended (warning if skipped)

**Actions**: Back, Next

#### Step 4: Sales Channel Connection (Optional)

**Prompt**: "Connect your first sales channel to start syncing data"

**Options**:
- Ozon (button)
- Wildberries (button)
- Custom Website (button)
- Skip for Now (link)

**Behavior**: Clicking marketplace opens credential input modal (same as Tab 2 in Import page)

**Actions**: Back, Finish Setup

#### Completion Screen

**Content**:
- Success message: "Your account is ready!"
- Summary of setup:
  - Company name
  - Warehouses created
  - Products imported
  - Channels connected
- "Go to Dashboard" button (primary CTA)
- "Watch Tutorial" link (optional, opens help video)

### 4.10 No Company Assignment Page (no_company.html)

**Page Objective**: Error state handling for users not assigned to a company

**Access Context**: 
- Displayed when authenticated user has no company relationship
- Prevents access to main application

**Page Layout**: Centered content, minimal navigation

**Content Elements**:

**Error Icon**: Large informational icon (not alarming, neutral color)

**Primary Message**: "No Company Assigned"

**Explanation Text**: 
"Your account is not currently associated with a company. Please contact your administrator to grant access, or create a new company to get started."

**Action Options**:

| Action | Button Style | Behavior |
|--------|--------------|----------|
| Create New Company | Primary | Redirects to wizard.html (Step 1) |
| Contact Support | Secondary | Opens email client or support form |
| Logout | Text link | Logs out user |

**Conditional Display**:
- If user is superuser/admin: Show "Create New Company" button
- If user is regular user: Hide create button, emphasize contact administrator

## 5. Integration with Existing System

### 5.1 Backend API Contract

**Frontend communicates with Django backend via RESTful API**

**Key Endpoints**:

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/api/dashboard/metrics/` | GET | Fetch KPI data | None | JSON with metrics object |
| `/api/products/` | GET | List products with filters | Query params | Paginated product list |
| `/api/products/{id}/` | GET | Product detail | None | Complete product object |
| `/api/inventory/adjust/` | POST | Stock adjustment | Operation details | Success/error status |
| `/api/inventory/movements/` | GET | Movement history | Filter params | Paginated movement list |
| `/api/warehouses/` | GET/POST | Warehouse CRUD | Warehouse object | Warehouse data |
| `/api/import/products/` | POST | Bulk import | Multipart file upload | Import job ID |
| `/api/integrations/sync/` | POST | Trigger marketplace sync | Marketplace ID | Sync job status |

**Authentication**: 
- Django session-based authentication (cookies)
- CSRF token required for state-changing operations

**Data Format**: JSON request/response bodies

**Error Handling**:
- HTTP status codes: 200 (success), 400 (validation error), 401 (unauthorized), 500 (server error)
- Error response format:
```
{
  "success": false,
  "error": "Error message",
  "field_errors": {"field_name": ["error detail"]}
}
```

### 5.2 State Management Strategy

**Redux Store Slices**:

| Slice | State Contents | Purpose |
|-------|---------------|---------|
| auth | User object, company, permissions | Authentication state |
| products | Product list, filters, selected product | Product catalog state |
| inventory | Warehouse data, stock levels | Inventory state |
| dashboard | Cached metrics, charts data | Dashboard state |
| ui | Modals, notifications, loading states | UI control state |

**Data Fetching Pattern**:
- On component mount: Fetch data if not in store or stale
- On user action: Optimistic updates with rollback on error
- Real-time updates: Polling every 30 seconds for dashboard metrics
- Cache invalidation: On successful write operations

### 5.3 Routing Structure

**Route Mapping**:

| Path | Component | Auth Required | Access Control |
|------|-----------|---------------|----------------|
| `/` | Dashboard | Yes | Has company |
| `/onboarding` | Wizard | Yes | No company |
| `/products` | AllProducts | Yes | Has company |
| `/products/:id` | ProductDetail (modal) | Yes | Has company |
| `/inventory` | InventoryOverview | Yes | Has company |
| `/inventory/warehouse/:id` | WarehouseInventory | Yes | Has company |
| `/inventory/adjust` | StockAdjustment | Yes | Has company |
| `/inventory/history` | MovementHistory | Yes | Has company |
| `/settings/company` | CompanySettings | Yes | Admin role |
| `/settings/warehouses` | WarehouseManagement | Yes | Has company |
| `/settings/import` | ProductImport | Yes | Has company |
| `/no-company` | NoCompany | Yes | No company |

**Route Guards**:
- Check authentication status
- Check company assignment (redirect to /no-company if missing)
- Check user permissions for admin routes

### 5.4 Responsive Design Strategy

**Breakpoints**:

| Device | Width | Layout Adjustments |
|--------|-------|-------------------|
| Desktop | > 1200px | Full sidebar, multi-column dashboards |
| Tablet | 768px - 1199px | Collapsible sidebar, 2-column layouts |
| Mobile | < 768px | Hamburger menu, single column, simplified tables |

**Mobile-Specific Adaptations**:
- Sidebar converts to slide-out drawer
- Tables convert to card list views on small screens
- Hide less critical columns
- Sticky action buttons at bottom
- Touch-optimized button sizes (min 44x44px)

## 6. Component Reusability Map

**Shared Components**:

| Component Name | Used In | Props |
|---------------|---------|-------|
| ProductCard | All Products, Dashboard | product, onClick, actions |
| StockBadge | All tables | daysRemaining, size |
| MovementTypeIcon | History, Activity Feed | type, size |
| WarehouseSelector | Inventory pages | selectedId, onChange |
| FilterPanel | Products, History | filters, onApply |
| DataTable | All listing pages | columns, data, actions |
| ImportWizard | Import page, Onboarding | onComplete |

## 7. Performance Optimization Strategies

**Frontend Performance**:

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| Code Splitting | React.lazy() for route components | Reduced initial bundle size |
| Virtual Scrolling | For tables with 500+ rows | Smooth rendering of large datasets |
| Debounced Search | 300ms delay on search input | Reduced API calls |
| Memoization | React.memo for expensive components | Prevent unnecessary re-renders |
| Image Optimization | Lazy loading, thumbnail CDN | Faster page loads |
| API Response Caching | 5-minute cache for reference data | Reduced server load |

**Bundle Size Target**: < 500KB gzipped initial load

## 8. Accessibility Compliance

**WCAG 2.1 Level AA Requirements**:

- Keyboard navigation for all interactive elements
- ARIA labels for icon-only buttons
- Color contrast ratio minimum 4.5:1
- Focus indicators visible on all focusable elements
- Screen reader-friendly table markup
- Alt text for all images
- Form field labels and error associations

**Testing**: Automated accessibility audits with Axe DevTools

## 9. Error Handling & User Feedback

**Error Categories**:

| Error Type | User Feedback | Technical Action |
|------------|---------------|------------------|
| Network Error | Toast: "Connection lost. Retrying..." | Auto-retry with exponential backoff |
| Validation Error | Inline field errors in red | Highlight fields, scroll to first error |
| Server Error | Modal: "Something went wrong" with details | Log to error tracking service |
| Permission Denied | Redirect to login or show access denied message | Check auth state |

**Success Feedback**:
- Toast notifications for completed actions
- Inline success messages
- Visual confirmation (checkmark icons, green highlights)

**Loading States**:
- Skeleton loaders for content areas
- Spinner overlays for form submissions
- Progress bars for file uploads and imports

## 10. Localization Readiness

**Current Implementation**: English interface

**Future Localization Support**:

- All UI strings externalized to i18n library (react-i18next)
- Date/time formatting via Day.js with locale support
- Number/currency formatting via Intl.NumberFormat
- RTL layout support for Arabic/Hebrew (future)

**Primary Target Locale**: Russian (ru-RU)

**Localization Scope**:
- Interface labels and messages
- Error messages
- Email templates
- Documentation and help text

## 11. Design System Governance

**Component Library Maintenance**:
- Centralized theme configuration (colors, spacing, typography)
- Shared Ant Design theme customization
- Reusable component documentation (Storybook recommended)

**Design Consistency Checks**:
- Figma design system as source of truth
- Regular design-code sync reviews
- Automated visual regression testing

## 12. Deployment Considerations

**Build Process**:
- Production build: `npm run build`
- Environment-specific configs (.env files)
- Asset optimization (minification, tree-shaking)

**Hosting Strategy**:
- Static file serving via Django (collectstatic)
- OR separate CDN deployment for frontend assets
- Service Worker for offline capability (future enhancement)

**Browser Support**:
- Modern browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)
- Graceful degradation for older browsers

## 13. Future Enhancements Roadmap

**Phase 2.0 Features** (mentioned in original requirements):

- Forecasting & Orders section with automated procurement workflows
- Advanced Reports module with custom report builder
- Real-time dashboard updates via WebSocket
- Mobile application (React Native)
- Advanced analytics with predictive insights

**Phase 3.0 Considerations**:
- Multi-currency support with real-time exchange rates
- Advanced user permissions and role-based access control
- API for third-party integrations
- White-label customization capabilities
