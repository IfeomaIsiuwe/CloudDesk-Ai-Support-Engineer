"""
Notification Handler - Manage notifications and alerts
"""
from database import DatabaseManager
from typing import List, Dict, Optional
from datetime import datetime


class NotificationHandler:
    """Manages notifications and alerts"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def notify_escalation(self, user_id: str, query_id: str) -> str:
        """Notify user of escalation"""
        query = self.db.get_query(query_id)
        message = f"Your query '{query['question'][:50]}...' has been escalated to our support team."
        
        return self.db.insert_notification(
            user_id,
            "escalation",
            message,
            "in_app"
        )
    
    def notify_resolution(self, user_id: str, ticket_id: str) -> str:
        """Notify user of resolution"""
        message = "Your escalated query has been resolved. Please check your inbox for details."
        
        return self.db.insert_notification(
            user_id,
            "resolution",
            message,
            "in_app"
        )
    
    def notify_tier2_assignment(self, user_id: str, support_agent: str) -> str:
        """Notify user of tier 2 assignment"""
        message = f"Your query has been assigned to {support_agent} for priority support."
        
        return self.db.insert_notification(
            user_id,
            "assignment",
            message,
            "in_app"
        )
    
    def get_unread_notifications(self, user_id: str) -> List[Dict]:
        """Get unread notifications for user"""
        return self.db.get_unread_notifications(user_id)
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        sql = """
            UPDATE notifications
            SET read = TRUE
            WHERE id = ?
        """
        return self.db.execute_update(sql, (notification_id,)) > 0
    
    def get_notification_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get notification history"""
        sql = """
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY sent_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (user_id, limit))
    
    def send_batch_notification(self, user_ids: List[str], message: str, 
                               notification_type: str = "info") -> int:
        """Send notification to multiple users"""
        count = 0
        for user_id in user_ids:
            self.db.insert_notification(
                user_id,
                notification_type,
                message,
                "in_app"
            )
            count += 1
        return count
    
    def get_notification_summary(self, user_id: str) -> Dict:
        """Get notification summary for user"""
        sql = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN read = FALSE THEN 1 ELSE 0 END) as unread,
                notification_type,
                COUNT(*) as type_count
            FROM notifications
            WHERE user_id = ?
            GROUP BY notification_type
        """
        results = self.db.execute_query(sql, (user_id,))
        
        summary = {
            "total_notifications": 0,
            "unread_notifications": 0,
            "by_type": {}
        }
        
        for row in results:
            summary['total_notifications'] = row.get('total', 0) or 0
            summary['unread_notifications'] = row.get('unread', 0) or 0
            summary['by_type'][row['notification_type']] = row.get('type_count', 0) or 0
        
        return summary
    
    def delete_old_notifications(self, days: int = 90) -> int:
        """Delete notifications older than specified days"""
        sql = """
            DELETE FROM notifications
            WHERE sent_at < datetime('now', '-' || ? || ' days')
        """
        return self.db.execute_update(sql, (days,))
    
    def get_notification_engagement(self, days: int = 30) -> Dict:
        """Get notification engagement metrics"""
        sql = """
            SELECT 
                COUNT(*) as total_sent,
                SUM(CASE WHEN read = TRUE THEN 1 ELSE 0 END) as total_read,
                notification_type,
                CAST(COUNT(CASE WHEN read = TRUE THEN 1 END) AS FLOAT) / COUNT(*) * 100 as read_rate
            FROM notifications
            WHERE sent_at >= datetime('now', '-' || ? || ' days')
            GROUP BY notification_type
        """
        results = self.db.execute_query(sql, (days,))
        
        summary = {}
        for row in results:
            notif_type = row['notification_type']
            summary[notif_type] = {
                "total_sent": row.get('total_sent', 0) or 0,
                "total_read": row.get('total_read', 0) or 0,
                "read_rate_percentage": round(row.get('read_rate', 0) or 0, 2)
            }
        
        return summary
