"""
Database Manager - Handles all database operations
"""
import sqlite3
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from database.models import DATABASE_SCHEMA
import os


class DatabaseManager:
    """Manages all database connections and operations"""
    
    def __init__(self, db_path: str = "clouddesk.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executescript(DATABASE_SCHEMA)
            conn.commit()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def execute_query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            conn.close()
    
    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"✗ Update error: {e}")
            return 0
        finally:
            conn.close()
    
    # ==================== Query Operations ====================
    
    def insert_query(self, user_id: str, session_id: str, question: str) -> str:
        """Insert new query"""
        query_id = str(uuid.uuid4())
        sql = """
            INSERT INTO queries (id, user_id, session_id, question)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(sql, (query_id, user_id, session_id, question))
        return query_id
    
    def get_query(self, query_id: str) -> Optional[Dict]:
        """Get query by ID"""
        sql = "SELECT * FROM queries WHERE id = ?"
        results = self.execute_query(sql, (query_id,))
        return results[0] if results else None
    
    def get_user_queries(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's queries"""
        sql = """
            SELECT * FROM queries 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        return self.execute_query(sql, (user_id, limit))
    
    def update_query_status(self, query_id: str, status: str) -> int:
        """Update query status"""
        sql = """
            UPDATE queries 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        return self.execute_update(sql, (status, query_id))
    
    def update_query_category(self, query_id: str, category: str, tags: List[str]) -> int:
        """Update query category and tags"""
        tags_json = json.dumps(tags)
        sql = """
            UPDATE queries 
            SET category = ?, tags = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        return self.execute_update(sql, (category, tags_json, query_id))
    
    # ==================== Response Operations ====================
    
    def insert_response(self, query_id: str, answer: str, confidence: float,
                       response_time_ms: float, sources: List[str]) -> str:
        """Insert query response"""
        response_id = str(uuid.uuid4())
        sources_json = json.dumps(sources)
        sql = """
            INSERT INTO query_responses 
            (id, query_id, answer, confidence, response_time_ms, sources)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute_update(
            sql, (response_id, query_id, answer, confidence, response_time_ms, sources_json)
        )
        return response_id
    
    def get_response(self, response_id: str) -> Optional[Dict]:
        """Get response by ID"""
        sql = "SELECT * FROM query_responses WHERE id = ?"
        results = self.execute_query(sql, (response_id,))
        return results[0] if results else None
    
    def get_query_response(self, query_id: str) -> Optional[Dict]:
        """Get response for a query"""
        sql = "SELECT * FROM query_responses WHERE query_id = ? LIMIT 1"
        results = self.execute_query(sql, (query_id,))
        return results[0] if results else None
    
    # ==================== Feedback Operations ====================
    
    def insert_feedback(self, query_id: str, response_id: str, user_id: str,
                       rating: Optional[int] = None, helpful: bool = False,
                       comment: Optional[str] = None) -> str:
        """Insert feedback"""
        feedback_id = str(uuid.uuid4())
        sql = """
            INSERT INTO feedback (id, query_id, response_id, user_id, rating, helpful, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_update(sql, (feedback_id, query_id, response_id, user_id, rating, helpful, comment))
        return feedback_id
    
    def get_feedback(self, query_id: str) -> Optional[Dict]:
        """Get feedback for a query"""
        sql = "SELECT * FROM feedback WHERE query_id = ? LIMIT 1"
        results = self.execute_query(sql, (query_id,))
        return results[0] if results else None
    
    def get_avg_rating(self, days: int = 30) -> float:
        """Get average rating for period"""
        sql = """
            SELECT AVG(rating) as avg_rating 
            FROM feedback 
            WHERE rating IS NOT NULL 
            AND created_at >= datetime('now', '-' || ? || ' days')
        """
        results = self.execute_query(sql, (days,))
        return results[0]['avg_rating'] or 0.0 if results else 0.0
    
    # ==================== Learned Responses Operations ====================
    
    def insert_learned_response(self, original_query_id: str, tier2_response: str,
                               category: str, tags: List[str]) -> str:
        """Insert learned response from Tier 2"""
        learned_id = str(uuid.uuid4())
        tags_json = json.dumps(tags)
        sql = """
            INSERT INTO learned_responses (id, original_query_id, tier2_response, category, tags)
            VALUES (?, ?, ?, ?, ?)
        """
        self.execute_update(sql, (learned_id, original_query_id, tier2_response, category, tags_json))
        return learned_id
    
    def get_learned_responses_by_category(self, category: str) -> List[Dict]:
        """Get learned responses by category"""
        sql = """
            SELECT * FROM learned_responses 
            WHERE category = ? AND is_active = TRUE
        """
        return self.execute_query(sql, (category,))
    
    def increment_learned_response_usage(self, learned_id: str) -> int:
        """Increment usage count for learned response"""
        sql = """
            UPDATE learned_responses 
            SET times_reused = times_reused + 1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        return self.execute_update(sql, (learned_id,))
    
    # ==================== Escalation Operations ====================
    
    def insert_escalation(self, query_id: str, reason: str, priority: str = "medium") -> str:
        """Insert escalation ticket"""
        ticket_id = str(uuid.uuid4())
        sql = """
            INSERT INTO escalation_tickets (id, query_id, reason, priority)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(sql, (ticket_id, query_id, reason, priority))
        # Update query status
        self.update_query_status(query_id, "escalated")
        return ticket_id
    
    def get_escalation_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get escalation ticket"""
        sql = "SELECT * FROM escalation_tickets WHERE id = ?"
        results = self.execute_query(sql, (ticket_id,))
        return results[0] if results else None
    
    def get_open_escalations(self, limit: int = 100) -> List[Dict]:
        """Get open escalation tickets"""
        sql = """
            SELECT et.*, q.question, u.username 
            FROM escalation_tickets et
            JOIN queries q ON et.query_id = q.id
            JOIN users u ON q.user_id = u.id
            WHERE et.status = 'open'
            ORDER BY et.created_at DESC
            LIMIT ?
        """
        return self.execute_query(sql, (limit,))
    
    def update_escalation_response(self, ticket_id: str, tier2_response: str) -> int:
        """Update escalation with Tier 2 response"""
        sql = """
            UPDATE escalation_tickets 
            SET tier2_response = ?, status = 'resolved', resolved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.execute_update(sql, (tier2_response, ticket_id))
    
    # ==================== Session Operations ====================
    
    def insert_session(self, user_id: str) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        sql = "INSERT INTO sessions (id, user_id) VALUES (?, ?)"
        self.execute_update(sql, (session_id, user_id))
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session"""
        sql = "SELECT * FROM sessions WHERE id = ?"
        results = self.execute_query(sql, (session_id,))
        return results[0] if results else None
    
    def update_session_stats(self, session_id: str, query_count: int, 
                            escalation_count: int, response_time_ms: float) -> int:
        """Update session statistics"""
        sql = """
            UPDATE sessions 
            SET query_count = ?, escalation_count = ?, total_response_time_ms = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.execute_update(sql, (query_count, escalation_count, response_time_ms, session_id))
    
    def end_session(self, session_id: str) -> int:
        """End user session"""
        sql = "UPDATE sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.execute_update(sql, (session_id,))
    
    # ==================== User Operations ====================
    
    def insert_user(self, username: str, email: str, role: str = "customer") -> str:
        """Create new user"""
        user_id = str(uuid.uuid4())
        sql = """
            INSERT INTO users (id, username, email, role)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(sql, (user_id, username, email, role))
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        sql = "SELECT * FROM users WHERE id = ?"
        results = self.execute_query(sql, (user_id,))
        return results[0] if results else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        sql = "SELECT * FROM users WHERE email = ?"
        results = self.execute_query(sql, (email,))
        return results[0] if results else None
    
    # ==================== Metrics Operations ====================
    
    def get_metrics_summary(self, days: int = 30) -> Dict:
        """Get metrics summary for period"""
        queries_sql = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) as escalated,
                AVG(CAST((SELECT confidence FROM query_responses WHERE query_id = queries.id LIMIT 1) AS REAL)) as avg_confidence
            FROM queries
            WHERE created_at >= datetime('now', '-' || ? || ' days')
        """
        
        response_time_sql = """
            SELECT AVG(response_time_ms) as avg_time
            FROM query_responses
            WHERE created_at >= datetime('now', '-' || ? || ' days')
        """
        
        users_sql = """
            SELECT COUNT(DISTINCT user_id) as unique_users
            FROM queries
            WHERE created_at >= datetime('now', '-' || ? || ' days')
        """
        
        queries_result = self.execute_query(queries_sql, (days,))[0]
        time_result = self.execute_query(response_time_sql, (days,))[0]
        users_result = self.execute_query(users_sql, (days,))[0]
        
        return {
            "total_queries": queries_result['total'] or 0,
            "resolved_queries": queries_result['resolved'] or 0,
            "escalated_queries": queries_result['escalated'] or 0,
            "avg_confidence": queries_result['avg_confidence'] or 0.0,
            "avg_response_time_ms": time_result['avg_time'] or 0.0,
            "unique_users": users_result['unique_users'] or 0,
            "period_days": days
        }
    
    def insert_performance_metric(self, metric_name: str, value: float, category: str = "system"):
        """Insert performance metric"""
        metric_id = str(uuid.uuid4())
        sql = """
            INSERT INTO performance_metrics (id, metric_name, value, category)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(sql, (metric_id, metric_name, value, category))
    
    # ==================== Cache Operations ====================
    
    def get_cached_response(self, query_hash: str) -> Optional[Dict]:
        """Get cached response"""
        sql = """
            SELECT result FROM cache_entries 
            WHERE query_hash = ? AND expires_at > CURRENT_TIMESTAMP
        """
        results = self.execute_query(sql, (query_hash,))
        if results:
            self.execute_update(
                "UPDATE cache_entries SET hit_count = hit_count + 1 WHERE query_hash = ?",
                (query_hash,)
            )
            return json.loads(results[0]['result'])
        return None
    
    def cache_response(self, query_hash: str, result: Dict, ttl_seconds: int = 86400):
        """Cache query response"""
        cache_id = str(uuid.uuid4())
        result_json = json.dumps(result)
        sql = """
            INSERT INTO cache_entries (id, query_hash, result, ttl_seconds)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(sql, (cache_id, query_hash, result_json, ttl_seconds))
    
    # ==================== Audit Log Operations ====================
    
    def insert_audit_log(self, user_id: str, action: str, resource_type: str,
                        resource_id: str, old_value: Optional[str] = None,
                        new_value: Optional[str] = None):
        """Insert audit log"""
        log_id = str(uuid.uuid4())
        sql = """
            INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, old_value, new_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_update(sql, (log_id, user_id, action, resource_type, resource_id, old_value, new_value))
    
    def get_audit_logs(self, resource_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get audit logs"""
        if resource_id:
            sql = """
                SELECT * FROM audit_logs 
                WHERE resource_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            return self.execute_query(sql, (resource_id, limit))
        else:
            sql = """
                SELECT * FROM audit_logs 
                ORDER BY timestamp DESC
                LIMIT ?
            """
            return self.execute_query(sql, (limit,))
    
    # ==================== Notification Operations ====================
    
    def insert_notification(self, user_id: str, notification_type: str, 
                           message: str, channel: str = "in_app"):
        """Insert notification"""
        notif_id = str(uuid.uuid4())
        sql = """
            INSERT INTO notifications (id, user_id, notification_type, message, channel)
            VALUES (?, ?, ?, ?, ?)
        """
        self.execute_update(sql, (notif_id, user_id, notification_type, message, channel))
    
    def get_unread_notifications(self, user_id: str) -> List[Dict]:
        """Get unread notifications"""
        sql = """
            SELECT * FROM notifications 
            WHERE user_id = ? AND read = FALSE
            ORDER BY sent_at DESC
        """
        return self.execute_query(sql, (user_id,))
    
    # ==================== Search Analytics Operations ====================
    
    def update_search_analytic(self, query: str, category: Optional[str] = None,
                              success: bool = True, escalated: bool = False):
        """Update search analytics"""
        sql = """
            SELECT * FROM search_analytics WHERE query = ? LIMIT 1
        """
        results = self.execute_query(sql, (query,))
        
        if results:
            analytic_id = results[0]['id']
            update_sql = """
                UPDATE search_analytics
                SET search_count = search_count + 1,
                    last_searched = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            self.execute_update(update_sql, (analytic_id,))
        else:
            analytic_id = str(uuid.uuid4())
            insert_sql = """
                INSERT INTO search_analytics (id, query, category, search_count)
                VALUES (?, ?, ?, 1)
            """
            self.execute_update(insert_sql, (analytic_id, query, category))
    
    def get_top_queries(self, limit: int = 10) -> List[Dict]:
        """Get most searched queries"""
        sql = """
            SELECT * FROM search_analytics
            ORDER BY search_count DESC
            LIMIT ?
        """
        return self.execute_query(sql, (limit,))
