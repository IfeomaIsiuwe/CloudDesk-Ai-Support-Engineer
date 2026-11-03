"""
Audit Logger - Compliance and audit trail management
"""
from database import DatabaseManager
from typing import List, Dict, Optional
from datetime import datetime


class AuditLogger:
    """Manages audit logs for compliance"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def log_action(self, user_id: str, action: str, resource_type: str, 
                   resource_id: str, old_value: Optional[str] = None,
                   new_value: Optional[str] = None):
        """Log an action for audit trail"""
        self.db.insert_audit_log(user_id, action, resource_type, resource_id, old_value, new_value)
    
    def get_audit_trail(self, resource_id: str, limit: int = 100) -> List[Dict]:
        """Get audit trail for a resource"""
        return self.db.get_audit_logs(resource_id, limit)
    
    def get_user_actions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all actions by a user"""
        sql = """
            SELECT * FROM audit_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (user_id, limit))
    
    def get_audit_summary(self, days: int = 30) -> Dict:
        """Get audit summary"""
        sql = """
            SELECT 
                COUNT(*) as total_actions,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT resource_type) as resource_types,
                COUNT(DISTINCT action) as action_types
            FROM audit_logs
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """
        results = self.db.execute_query(sql, (days,))
        result = results[0] if results else {}
        
        return {
            "total_actions": result.get('total_actions', 0) or 0,
            "unique_users": result.get('unique_users', 0) or 0,
            "resource_types": result.get('resource_types', 0) or 0,
            "action_types": result.get('action_types', 0) or 0,
            "period_days": days
        }
    
    def get_actions_by_type(self, days: int = 30) -> Dict[str, int]:
        """Get action distribution"""
        sql = """
            SELECT action, COUNT(*) as count
            FROM audit_logs
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY action
            ORDER BY count DESC
        """
        results = self.db.execute_query(sql, (days,))
        return {row['action']: row['count'] for row in results}
    
    def get_sensitive_operations(self, days: int = 30) -> List[Dict]:
        """Get sensitive operations (deletions, escalations, etc)"""
        sensitive_actions = ['delete', 'escalate', 'resolve', 'override', 'reassign']
        sql = """
            SELECT * FROM audit_logs
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            AND action IN ({})
            ORDER BY timestamp DESC
        """.format(','.join(['?' for _ in sensitive_actions]))
        
        params = [days] + sensitive_actions
        return self.db.execute_query(sql, tuple(params))
    
    def export_audit_log(self, start_date: str, end_date: str) -> List[Dict]:
        """Export audit logs for a date range"""
        sql = """
            SELECT * FROM audit_logs
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """
        return self.db.execute_query(sql, (start_date, end_date))
    
    def get_user_activity_timeline(self, user_id: str) -> List[Dict]:
        """Get user activity timeline"""
        sql = """
            SELECT 
                timestamp,
                action,
                resource_type,
                resource_id,
                old_value,
                new_value
            FROM audit_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """
        return self.db.execute_query(sql, (user_id,))
    
    def compliance_report(self, days: int = 90) -> Dict:
        """Generate compliance report"""
        audit_summary = self.get_audit_summary(days)
        actions_by_type = self.get_actions_by_type(days)
        
        return {
            "report_generated": datetime.utcnow().isoformat(),
            "period_days": days,
            "summary": audit_summary,
            "actions_by_type": actions_by_type,
            "high_risk_operations": len(self.get_sensitive_operations(days))
        }
