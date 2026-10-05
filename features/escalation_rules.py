"""
Escalation Rules Engine - Intelligent routing and escalation management
"""
from database import DatabaseManager
from typing import Optional, List, Dict, Any
from enum import Enum


class EscalationRules:
    """Manages escalation logic and routing"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def should_escalate(self, confidence: float, query_category: Optional[str] = None) -> bool:
        """Determine if query should be escalated"""
        # Base rule: confidence below 60%
        if confidence < 0.6:
            return True
        
        # Category-specific rules
        if query_category:
            return self._check_category_rules(query_category, confidence)
        
        return False
    
    def _check_category_rules(self, category: str, confidence: float) -> bool:
        """Check category-specific escalation rules"""
        # Define category-specific thresholds
        category_thresholds = {
            "critical": 0.85,
            "billing": 0.75,
            "account": 0.70,
            "technical": 0.65,
            "general": 0.60
        }
        
        threshold = category_thresholds.get(category, 0.60)
        return confidence < threshold
    
    def create_escalation(self, query_id: str, reason: str, priority: str = "medium") -> str:
        """Create escalation ticket"""
        ticket_id = self.db.insert_escalation(query_id, reason, priority)
        
        # Log escalation
        self.db.insert_audit_log(
            "system", "create_escalation", "escalation_ticket", ticket_id, None, reason
        )
        
        # Send notification
        query = self.db.get_query(query_id)
        if query:
            self.db.insert_notification(
                query['user_id'],
                "escalation",
                f"Your question has been escalated to our support team.",
                "in_app"
            )
        
        return ticket_id
    
    def get_escalation_queue(self, priority: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get escalation queue"""
        if priority:
            sql = """
                SELECT et.*, q.question, u.username, u.email
                FROM escalation_tickets et
                JOIN queries q ON et.query_id = q.id
                JOIN users u ON q.user_id = u.id
                WHERE et.status = 'open' AND et.priority = ?
                ORDER BY et.created_at ASC
                LIMIT ?
            """
            return self.db.execute_query(sql, (priority, limit))
        else:
            return self.db.get_open_escalations(limit)
    
    def assign_escalation(self, ticket_id: str, assigned_to_user_id: str) -> bool:
        """Assign escalation to a support agent"""
        sql = """
            UPDATE escalation_tickets
            SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        result = self.db.execute_update(sql, (assigned_to_user_id, ticket_id))
        
        if result > 0:
            self.db.insert_audit_log(
                "system", "assign_escalation", "escalation_ticket", ticket_id
            )
        
        return result > 0
    
    def resolve_escalation(self, ticket_id: str, tier2_response: str, 
                          resolution_notes: Optional[str] = None) -> bool:
        """Resolve an escalation"""
        self.db.update_escalation_response(ticket_id, tier2_response)
        
        ticket = self.db.get_escalation_ticket(ticket_id)
        if ticket:
            # Save as learned response
            from features.knowledge_updater import KnowledgeUpdater
            updater = KnowledgeUpdater(self.db)
            updater.save_tier2_response(
                ticket['query_id'],
                tier2_response,
                ticket['query_id'],  # Will update with category later
                []
            )
        
        return True
    
    def get_escalation_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get escalation statistics"""
        sql = """
            SELECT 
                COUNT(*) as total_escalations,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_escalations,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_escalations,
                AVG(CAST(CASE 
                    WHEN tier2_response_time IS NULL THEN 0 
                    ELSE (julianday(tier2_response_time) - julianday(created_at)) * 24 * 60
                END AS REAL)) as avg_response_time_minutes
            FROM escalation_tickets
            WHERE created_at >= datetime('now', '-' || ? || ' days')
        """
        results = self.db.execute_query(sql, (days,))
        result = results[0] if results else {}
        
        return {
            "total_escalations": result.get('total_escalations', 0) or 0,
            "open_escalations": result.get('open_escalations', 0) or 0,
            "resolved_escalations": result.get('resolved_escalations', 0) or 0,
            "avg_response_time_minutes": round(result.get('avg_response_time_minutes', 0) or 0, 2),
            "period_days": days
        }
    
    def get_escalation_by_category(self, days: int = 30) -> list:
        """Get escalation metrics by category"""
        sql = """
            SELECT 
                q.category,
                COUNT(DISTINCT et.id) as escalation_count,
                CAST(COUNT(DISTINCT et.id) AS FLOAT) / COUNT(DISTINCT q.id) * 100 as escalation_rate
            FROM escalation_tickets et
            JOIN queries q ON et.query_id = q.id
            WHERE et.created_at >= datetime('now', '-' || ? || ' days')
            AND q.category IS NOT NULL
            GROUP BY q.category
            ORDER BY escalation_count DESC
        """
        return self.db.execute_query(sql, (days,))
    
    def get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of escalation priorities"""
        sql = """
            SELECT priority, COUNT(*) as count
            FROM escalation_tickets
            WHERE status = 'open'
            GROUP BY priority
        """
        results = self.db.execute_query(sql)
        distribution = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for row in results:
            if row['priority'] in distribution:
                distribution[row['priority']] = row['count']
        
        return distribution
    
    def get_escalation_avg_resolution_time(self, days: int = 30) -> float:
        """Get average resolution time for escalations"""
        sql = """
            SELECT AVG(CAST((julianday(resolved_at) - julianday(created_at)) * 24 * 60 AS REAL)) as avg_minutes
            FROM escalation_tickets
            WHERE status = 'resolved'
            AND resolved_at IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
        """
        results = self.db.execute_query(sql, (days,))
        result = results[0] if results else {}
        return round(result.get('avg_minutes', 0) or 0, 2)
    
    def get_top_escalation_reasons(self, limit: int = 10) -> list:
        """Get most common escalation reasons"""
        sql = """
            SELECT reason, COUNT(*) as count
            FROM escalation_tickets
            WHERE status IN ('open', 'resolved')
            GROUP BY reason
            ORDER BY count DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,))
