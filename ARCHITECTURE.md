# StockPredictor - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Web Server                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Views      │  │  Templates   │  │   REST API   │         │
│  │  (HTML/JSON) │  │  (Dashboard) │  │  (JSON)      │         │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘         │
│         │                                     │                 │
│         └────────────────┬────────────────────┘                 │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Business Logic Layer                        │  │
│  │                                                          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐    │  │
│  │  │Accounts │ │Products │ │  Sales   │ │Forecasting│    │  │
│  │  │ Module  │ │ Module  │ │  Module  │ │  Module   │    │  │
│  │  └─────────┘ └─────────┘ └──────────┘ └──────────┘    │  │
│  │                                                          │  │
│  │  ┌──────────────┐            ┌───────────────┐         │  │
│  │  │ Integrations │            │  Procurement  │         │  │
│  │  │    Module    │            │     Module    │         │  │
│  │  └──────────────┘            └───────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                         │
│                                                                 │
│  Companies │ Users │ Products │ Sales │ Forecasts │ Orders     │
└─────────────────────────────────────────────────────────────────┘

                         ▲
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                    Celery Task Queue                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Sync Tasks   │  │ Forecast     │  │ Procurement  │         │
│  │ (6:00 AM)    │  │ Tasks        │  │ Analysis     │         │
│  │              │  │ (7:00 AM)    │  │ (7:30 AM)    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼───────┐                           │
│                    │  Celery Beat  │                           │
│                    │  (Scheduler)  │                           │
│                    └───────────────┘                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Redis Broker                               │
│                   (Task Queue Storage)                          │
└─────────────────────────────────────────────────────────────────┘

                         ▲
                         │
┌────────────────────────┴────────────────────────────────────────┐
│              External Marketplace APIs                          │
│                                                                 │
│    ┌──────────────────┐          ┌──────────────────┐          │
│    │  Wildberries API │          │     Ozon API     │          │
│    │                  │          │                  │          │
│    │  - Sales Data    │          │  - Sales Data    │          │
│    │  - Inventory     │          │  - Inventory     │          │
│    │  - Products      │          │  - Products      │          │
│    └──────────────────┘          └──────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Daily Synchronization Flow (6:00 AM)

```
Celery Beat → Trigger sync_all_marketplaces
     ↓
For each Company:
     ↓
     ├─→ Wildberries Client → Fetch Sales → Save to DB
     │                       → Fetch Inventory → Save to DB
     │                       → Fetch Products → Save to DB
     │
     └─→ Ozon Client → Fetch Sales → Save to DB
                     → Fetch Inventory → Save to DB
                     → Fetch Products → Save to DB
     ↓
Update DailySalesAggregate
```

### 2. Forecasting Flow (7:00 AM)

```
Celery Beat → Trigger generate_all_forecasts
     ↓
For each Product:
     ↓
     ├─→ Load Sales History (60-180 days)
     │
     ├─→ Feature Engineering:
     │   ├─ Lag features (1, 7, 14, 30 days)
     │   ├─ Rolling statistics (7, 14, 30 days)
     │   ├─ Calendar features (day_of_week, month, etc.)
     │   └─ Trend features
     │
     ├─→ Train/Update XGBoost Model
     │
     ├─→ Generate Predictions (7-30 days ahead)
     │
     └─→ Save to Forecast table with confidence intervals
```

### 3. Procurement Analysis Flow (7:30 AM)

```
Celery Beat → Trigger analyze_all_procurement
     ↓
For each Product:
     ↓
     ├─→ Get Current Inventory
     │
     ├─→ Calculate Daily Burn Rate
     │
     ├─→ Calculate Metrics:
     │   ├─ Runway Days = Stock / Burn Rate
     │   ├─ Stockout Date = Today + Runway Days
     │   └─ Recommended Quantity
     │
     ├─→ Check Existing Purchase Orders
     │
     ├─→ Categorize:
     │   ├─ ORDER_TODAY (runway ≤ threshold)
     │   ├─ ALREADY_ORDERED (PO covers demand)
     │   ├─ ATTENTION_REQUIRED (edge cases)
     │   └─ NORMAL
     │
     └─→ Save ProcurementRecommendation
```

## Module Dependencies

```
┌─────────────┐
│  Accounts   │
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│  Products   │    │Integrations │
└──────┬──────┘    └──────┬──────┘
       │                  │
       │    ┌─────────────┘
       │    │
       ▼    ▼
┌─────────────┐
│    Sales    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Forecasting │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Procurement │
└─────────────┘
```

## Key Design Patterns

### 1. Multi-Tenancy Pattern
- All models include `company_id` foreign key
- Query filtering by company enforced at ORM level
- Logical data isolation in single database

### 2. Strategy Pattern (Marketplace Clients)
- Abstract `MarketplaceClient` base class
- Concrete implementations: `WildberriesClient`, `OzonClient`
- Factory method: `get_client(marketplace, credentials)`

### 3. Repository Pattern (Analyzers)
- `ProcurementAnalyzer` encapsulates business logic
- Separation of data access from business rules
- Testable and maintainable

### 4. Task Queue Pattern
- Asynchronous processing with Celery
- Scheduled tasks with Celery Beat
- Retry logic and error handling

## Scalability Considerations

### Current Scale (Stage 1)
- 100-500 companies
- 1,000-10,000 SKUs per company
- Single server deployment

### Optimization Strategies
1. **Database Indexing**
   - Compound indexes on (company_id, date)
   - Indexes on foreign keys
   
2. **Query Optimization**
   - Prefetch related objects
   - Aggregate queries
   - Materialized views for daily aggregates

3. **Caching**
   - Dashboard data cached for 1 hour
   - Redis for session storage
   
4. **Task Distribution**
   - Parallel processing per product in Celery
   - Horizontal scaling of Celery workers

### Growth Path
- **Stage 2** (500-1000 companies): Add read replicas
- **Stage 3** (1000+ companies): Database sharding by company_id
- **Stage 4** (Enterprise): Consider microservices decomposition

## Security Layers

1. **Authentication**: Django session-based + email/password
2. **Authorization**: Company-level data isolation + role-based permissions
3. **API Security**: API token encryption (production)
4. **Data Encryption**: Marketplace credentials encrypted at rest
5. **HTTPS**: SSL/TLS for all communications (production)

## Monitoring & Observability

### Metrics to Track
- Sync success rate
- Forecast accuracy (MAPE)
- Procurement recommendation acceptance rate
- Dashboard load time
- Celery queue depth
- Database query performance

### Logging
- Structured logging with Python logging
- Celery task logs
- API request/response logs
- Error tracking (integrate Sentry for production)
