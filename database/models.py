"""
Database Models for CloudDesk AI Support System
Comprehensive schema for all features
"""
import datetime
from enum import Enum
from typing import Optional, List
import json


class QueryStatus(str, Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    PENDING = "pending"


class UserRole(str, Enum):
    CUSTOMER = "customer"
    SUPPORT = "support"
    TIER2 = "tier2"
    ADMIN = "admin"


class EscalationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseModel:
    """Base model with common fields"""
    
    def __init__(self):
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()

    def to_dict(self):
        return {
            k: v.isoformat() if isinstance(v, datetime.datetime) else v
            for k, v in self.__dict__.items()
        }


class Query(BaseModel):
    """Main query/ticket model"""
    
    def __init__(self, user_id: str, question: str, session_id: str):
        super().__init__()
        self.id: str = None  # Will be set by DB
        self.user_id = user_id
        self.session_id = session_id
        self.question = question
        self.status = QueryStatus.PENDING
        self.category: Optional[str] = None
        self.tags: List[str] = []
        self.embedding_vector: Optional[List[float]] = None
        self.requires_escalation = False
        self.priority = EscalationPriority.MEDIUM


class QueryResponse(BaseModel):
    """Response from RAG system"""
    
    def __init__(self, query_id: str, answer: str, confidence: float):
        super().__init__()
        self.id: str = None
        self.query_id = query_id
        self.answer = answer
        self.confidence = confidence
        self.response_time_ms: float = 0
        self.sources: List[str] = []
        self.model_used: str = "default"
        self.is_from_learned_kb = False
        self.learned_response_id: Optional[str] = None


class Feedback(BaseModel):
    """User feedback on responses"""
    
    def __init__(self, query_id: str, response_id: str, user_id: str):
        super().__init__()
        self.id: str = None
        self.query_id = query_id
        self.response_id = response_id
        self.user_id = user_id
        self.rating: Optional[int] = None  # 1-5 stars
        self.helpful = False  # Thumbs up/down
        self.comment: Optional[str] = None
        self.needs_improvement = False


class LearnedResponse(BaseModel):
    """Knowledge from Tier 2 responses"""
    
    def __init__(self, original_query_id: str, tier2_response: str, category: str):
        super().__init__()
        self.id: str = None
        self.original_query_id = original_query_id
        self.tier2_response = tier2_response
        self.category = category
        self.tags: List[str] = []
        self.confidence_threshold = 0.6
        self.times_reused = 0
        self.is_active = True
        self.embedding_vector: Optional[List[float]] = None


class EscalationTicket(BaseModel):
    """Escalation to Tier 2"""
    
    def __init__(self, query_id: str, reason: str, assigned_to: Optional[str] = None):
        super().__init__()
        self.id: str = None
        self.query_id = query_id
        self.reason = reason
        self.assigned_to = assigned_to
        self.priority = EscalationPriority.MEDIUM
        self.status = "open"
        self.tier2_response: Optional[str] = None
        self.tier2_response_time: Optional[datetime.datetime] = None
        self.resolved_at: Optional[datetime.datetime] = None
        self.resolution_notes: Optional[str] = None


class Session(BaseModel):
    """User session/conversation"""
    
    def __init__(self, user_id: str):
        super().__init__()
        self.id: str = None
        self.user_id = user_id
        self.query_count = 0
        self.escalation_count = 0
        self.total_response_time_ms = 0
        self.ended_at: Optional[datetime.datetime] = None
        self.metadata: dict = {}


class User(BaseModel):
    """User profile"""
    
    def __init__(self, username: str, email: str):
        super().__init__()
        self.id: str = None
        self.username = username
        self.email = email
        self.role = UserRole.CUSTOMER
        self.organization: Optional[str] = None
        self.is_active = True
        self.metadata: dict = {}


class Metrics(BaseModel):
    """System metrics and analytics"""
    
    def __init__(self):
        super().__init__()
        self.id: str = None
        self.timestamp = datetime.datetime.utcnow()
        self.total_queries = 0
        self.resolved_queries = 0
        self.escalated_queries = 0
        self.avg_confidence = 0.0
        self.avg_response_time_ms = 0.0
        self.unique_users = 0
        self.feedback_avg_rating = 0.0
        self.learned_responses_count = 0


class PerformanceMetric(BaseModel):
    """Performance tracking"""
    
    def __init__(self, metric_name: str, value: float):
        super().__init__()
        self.id: str = None
        self.metric_name = metric_name
        self.value = value
        self.timestamp = datetime.datetime.utcnow()
        self.category = "system"  # system, api, db, model


class AuditLog(BaseModel):
    """Audit trail for compliance"""
    
    def __init__(self, user_id: str, action: str, resource_type: str, resource_id: str):
        super().__init__()
        self.id: str = None
        self.user_id = user_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.old_value: Optional[str] = None
        self.new_value: Optional[str] = None
        self.ip_address: Optional[str] = None
        self.timestamp = datetime.datetime.utcnow()


class CacheEntry(BaseModel):
    """Query cache for optimization"""
    
    def __init__(self, query_hash: str, result: dict):
        super().__init__()
        self.id: str = None
        self.query_hash = query_hash
        self.result = json.dumps(result)
        self.hit_count = 0
        self.ttl_seconds = 86400  # 24 hours
        self.expires_at = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=86400
        )


class NotificationLog(BaseModel):
    """Notification tracking"""
    
    def __init__(self, user_id: str, notification_type: str, message: str):
        super().__init__()
        self.id: str = None
        self.user_id = user_id
        self.notification_type = notification_type
        self.message = message
        self.channel = "in_app"  # in_app, email, slack
        self.read = False
        self.sent_at = datetime.datetime.utcnow()


class APIKey(BaseModel):
    """API key management"""
    
    def __init__(self, user_id: str, name: str):
        super().__init__()
        self.id: str = None
        self.user_id = user_id
        self.name = name
        self.key_hash: str = None  # Will be hashed
        self.is_active = True
        self.last_used: Optional[datetime.datetime] = None
        self.rate_limit = 1000


class SearchAnalytic(BaseModel):
    """Search and query analytics"""
    
    def __init__(self, query: str, category: Optional[str] = None):
        super().__init__()
        self.id: str = None
        self.query = query
        self.category = category
        self.search_count = 0
        self.avg_response_time_ms = 0.0
        self.success_rate = 0.0
        self.escalation_rate = 0.0
        self.last_searched = datetime.datetime.utcnow()


# Database schema SQL
DATABASE_SCHEMA = """
-- Queries table
CREATE TABLE IF NOT EXISTS queries (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    category TEXT,
    tags TEXT,
    requires_escalation BOOLEAN DEFAULT FALSE,
    priority TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Query responses
CREATE TABLE IF NOT EXISTS query_responses (
    id TEXT PRIMARY KEY,
    query_id TEXT NOT NULL,
    answer TEXT NOT NULL,
    confidence REAL NOT NULL,
    response_time_ms REAL DEFAULT 0,
    sources TEXT,
    model_used TEXT DEFAULT 'default',
    is_from_learned_kb BOOLEAN DEFAULT FALSE,
    learned_response_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id),
    FOREIGN KEY (learned_response_id) REFERENCES learned_responses(id)
);

-- Feedback
CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    query_id TEXT NOT NULL,
    response_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    rating INTEGER,
    helpful BOOLEAN DEFAULT FALSE,
    comment TEXT,
    needs_improvement BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id),
    FOREIGN KEY (response_id) REFERENCES query_responses(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Learned responses
CREATE TABLE IF NOT EXISTS learned_responses (
    id TEXT PRIMARY KEY,
    original_query_id TEXT NOT NULL,
    tier2_response TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT,
    confidence_threshold REAL DEFAULT 0.6,
    times_reused INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_query_id) REFERENCES queries(id)
);

-- Escalation tickets
CREATE TABLE IF NOT EXISTS escalation_tickets (
    id TEXT PRIMARY KEY,
    query_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    assigned_to TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    tier2_response TEXT,
    tier2_response_time TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    query_count INTEGER DEFAULT 0,
    escalation_count INTEGER DEFAULT 0,
    total_response_time_ms REAL DEFAULT 0,
    ended_at TIMESTAMP,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT DEFAULT 'customer',
    organization TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metrics
CREATE TABLE IF NOT EXISTS metrics (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_queries INTEGER DEFAULT 0,
    resolved_queries INTEGER DEFAULT 0,
    escalated_queries INTEGER DEFAULT 0,
    avg_confidence REAL DEFAULT 0.0,
    avg_response_time_ms REAL DEFAULT 0.0,
    unique_users INTEGER DEFAULT 0,
    feedback_avg_rating REAL DEFAULT 0.0,
    learned_responses_count INTEGER DEFAULT 0
);

-- Performance metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id TEXT PRIMARY KEY,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    category TEXT DEFAULT 'system',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Cache entries
CREATE TABLE IF NOT EXISTS cache_entries (
    id TEXT PRIMARY KEY,
    query_hash TEXT UNIQUE NOT NULL,
    result TEXT NOT NULL,
    hit_count INTEGER DEFAULT 0,
    ttl_seconds INTEGER DEFAULT 86400,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    message TEXT NOT NULL,
    channel TEXT DEFAULT 'in_app',
    read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- API Keys
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP,
    rate_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Search analytics
CREATE TABLE IF NOT EXISTS search_analytics (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    category TEXT,
    search_count INTEGER DEFAULT 0,
    avg_response_time_ms REAL DEFAULT 0.0,
    success_rate REAL DEFAULT 0.0,
    escalation_rate REAL DEFAULT 0.0,
    last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_session_id ON queries(session_id);
CREATE INDEX IF NOT EXISTS idx_queries_status ON queries(status);
CREATE INDEX IF NOT EXISTS idx_responses_query_id ON query_responses(query_id);
CREATE INDEX IF NOT EXISTS idx_feedback_query_id ON feedback(query_id);
CREATE INDEX IF NOT EXISTS idx_escalations_query_id ON escalation_tickets(query_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalation_tickets(status);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
"""
