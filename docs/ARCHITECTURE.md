# CloudDesk AI Support System - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Main App        │  │  Admin Dashboard │  │ Analytics Dash   │ │
│  │ (streamlit)      │  │  (streamlit)     │  │  (streamlit)     │ │
│  │  Port: 8501      │  │  Port: 8502      │  │  Port: 8503      │ │
│  └─────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘ │
│            │                    │                      │           │
└────────────┼────────────────────┼──────────────────────┼───────────┘
             │                    │                      │
             └────────────────────┼──────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │    REST API (Flask)        │
                    │ Port: 5000                 │
                    │ 50+ Endpoints              │
                    └─────────────┬──────────────┘
                                  │
        ┌─────────────────────────┴─────────────────────────┐
        │                                                   │
┌───────▼────────────────────────────────────────────────────────────┐
│              FEATURE MODULES (11 Total)                            │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Core Processing                                             │ │
│  │  • Metrics Tracker        - Stats & analytics               │ │
│  │  • Feedback System        - User ratings                    │ │
│  │  • Knowledge Updater      - Learn from Tier 2               │ │
│  │  • Session Manager        - Chat history                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Intelligent Systems                                         │ │
│  │  • Escalation Rules       - Smart routing                   │ │
│  │  • Cache Manager          - Performance                     │ │
│  │  • Tagging System         - Auto-categorization             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Management & Compliance                                     │ │
│  │  • Notification Handler   - Alerts                          │ │
│  │  • Audit Logger           - Compliance trail                │ │
│  │  • Search Analytics       - Query insights                  │ │
│  │  • User Manager           - Profiles & roles                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
        ┌───────────────────────▼────────────────────┐
        │      DATABASE LAYER (SQLite)               │
        │                                            │
        │  ┌────────────────────────────────────┐   │
        │  │ 14 Tables:                          │   │
        │  │  • queries                          │   │
        │  │  • query_responses                  │   │
        │  │  • feedback                         │   │
        │  │  • learned_responses                │   │
        │  │  • escalation_tickets               │   │
        │  │  • sessions                         │   │
        │  │  • users                            │   │
        │  │  • cache_entries                    │   │
        │  │  • notifications                    │   │
        │  │  • audit_logs                       │   │
        │  │  • api_keys                         │   │
        │  │  • search_analytics                 │   │
        │  │  • performance_metrics              │   │
        │  │  • metrics                          │   │
        │  └────────────────────────────────────┘   │
        │                                            │
        │  File: clouddesk.db                       │
        └────────────────────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   RAG PIPELINE                      │
        │   (retrieval_pipeline.py)           │
        │                                     │
        │  • Vector Database (Pinecone)       │
        │  • LLM (Hugging Face)               │
        │  • Embeddings                       │
        │  • Knowledge Base                   │
        └─────────────────────────────────────┘
```

## Data Flow

```
User Query
    │
    ├─► Auto-categorize (Tagging System)
    │
    ├─► Check cache (Cache Manager)
    │   ├─ Cache hit? ──► Return cached response
    │   │
    │   └─ Cache miss? ──┐
    │                    │
    │                    ├─► RAG Pipeline (LLM + Vector DB)
    │                    │
    │                    ├─► Store response (Database)
    │                    │
    │                    ├─► Cache result (Cache Manager)
    │
    ├─► Check escalation (Escalation Rules)
    │   ├─ Low confidence? ──► Create escalation ticket
    │   │
    │   └─ High confidence? ──► Continue
    │
    ├─► Record metrics (Metrics Tracker)
    │
    ├─► Record search (Search Analytics)
    │
    ├─► User feedback (Feedback System)
    │
    └─► Learn from Tier 2 (Knowledge Updater)
```

## Component Interactions

```
┌─────────────┐
│  Streamlit  │─────────────────────────┐
│    Apps     │                         │
└─────────────┘                         │
                                        │
┌─────────────┐      ┌──────────────────▼──────┐
│  REST API   │─────▶│   Feature Modules       │
│  (Flask)    │      │  (11 independent       │
└─────────────┘      │   modules)             │
                     └──────────┬──────────────┘
                                │
                     ┌──────────▼───────────┐
                     │  Database Manager    │
                     │  (SQLite)            │
                     └──────────┬───────────┘
                                │
                     ┌──────────▼───────────┐
                     │  RAG Pipeline        │
                     │  • LLM               │
                     │  • Vector DB         │
                     │  • Knowledge Base    │
                     └──────────────────────┘
```

## Deployment Architecture

```
┌───────────────────────────────────────────────────────────┐
│                  Production Deployment                     │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Streamlit    │  │ Streamlit    │  │ Streamlit    │   │
│  │ Main App     │  │ Admin Dash   │  │ Analytics    │   │
│  │ (systemd)    │  │ (systemd)    │  │ (systemd)    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│  ┌──────▼─────────────────▼─────────────────▼──────┐    │
│  │         Gunicorn (WSGI Server)                   │    │
│  │         4 worker processes                      │    │
│  │         Flask API (Port 5000)                   │    │
│  └──────────────────┬─────────────────────────────┘    │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │         Reverse Proxy (Nginx)                   │   │
│  │         Load balancing                          │   │
│  │         SSL/TLS termination                     │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  SQLite Database (clouddesk.db)                 │   │
│  │  Backup: /backups/clouddesk_*.db               │   │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Integration Points

```
CloudDesk System
├── External Integrations
│   ├─ Hugging Face API (LLM)
│   ├─ Pinecone (Vector DB)
│   ├─ Slack (notifications)
│   ├─ Email Service (alerts)
│   └─ Analytics Platforms
│
├── Client Systems
│   ├─ Web Applications
│   ├─ Mobile Apps
│   ├─ Chatbots
│   ├─ Support Platforms
│   └─ Custom Tools
│
└── Data Destinations
    ├─ Data Warehouse
    ├─ BI Tools
    ├─ Reporting Systems
    └─ Compliance Platforms
```

## Security Architecture

```
┌─────────────────────────────────────────────────┐
│            Security Layers                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Authentication                             │
│     ├─ API Key validation                      │
│     ├─ User sessions                           │
│     └─ OAuth integration ready                 │
│                                                │
│  2. Authorization                              │
│     ├─ Role-based access control               │
│     ├─ Admin, Tier2, Support, Customer         │
│     └─ Resource-level permissions              │
│                                                │
│  3. Audit & Compliance                         │
│     ├─ All actions logged                      │
│     ├─ Sensitive operations tracked            │
│     ├─ Compliance reports                      │
│     └─ Data retention policies                 │
│                                                │
│  4. Data Protection                            │
│     ├─ Password hashing                        │
│     ├─ API key encryption                      │
│     ├─ Database backups                        │
│     └─ GDPR compliance                         │
│                                                │
└─────────────────────────────────────────────────┘
```

## Scaling Strategy

```
Single Server (Development)
    │
    └─► Vertical Scaling (Larger instance)
        │
        └─► Horizontal Scaling (Multiple instances)
            │
            ├─► Load Balancer (Nginx)
            ├─► API Server Farm (Gunicorn)
            ├─► Cache Layer (Redis)
            ├─► Database Cluster (PostgreSQL)
            ├─► Vector DB (Pinecone)
            └─► Monitoring & Logging (ELK)
```

---

**Architecture Version:** 1.0  
**Last Updated:** October 2026  
**Status:** Production Ready ✅
