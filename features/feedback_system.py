"""
Feedback System - Collects and analyzes user feedback
"""
from database import DatabaseManager
from typing import Optional, Dict, Any


class FeedbackSystem:
    """Manages user feedback on responses"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def submit_feedback(self, query_id: str, response_id: str, user_id: str,
                       rating: Optional[int] = None, helpful: bool = False,
                       comment: Optional[str] = None) -> str:
        """Submit feedback on a response"""
        feedback_id = self.db.insert_feedback(
            query_id, response_id, user_id, rating, helpful, comment
        )
        return feedback_id
    
    def get_feedback(self, query_id: str) -> Optional[Dict]:
        """Get feedback for a query"""
        return self.db.get_feedback(query_id)
    
    def get_rating_distribution(self, days: int = 30) -> Dict[int, int]:
        """Get distribution of ratings"""
        sql = """
            SELECT rating, COUNT(*) as count
            FROM feedback
            WHERE rating IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY rating
            ORDER BY rating
        """
        results = self.db.execute_query(sql, (days,))
        distribution = {i: 0 for i in range(1, 6)}
        for row in results:
            if row['rating']:
                distribution[row['rating']] = row['count']
        return distribution
    
    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback summary"""
        sql = """
            SELECT 
                COUNT(*) as total_feedback,
                SUM(CASE WHEN helpful = 1 THEN 1 ELSE 0 END) as helpful_count,
                SUM(CASE WHEN helpful = 0 THEN 1 ELSE 0 END) as unhelpful_count,
                AVG(CAST(rating AS REAL)) as avg_rating,
                SUM(CASE WHEN needs_improvement = 1 THEN 1 ELSE 0 END) as needs_improvement_count
            FROM feedback
            WHERE created_at >= datetime('now', '-' || ? || ' days')
        """
        results = self.db.execute_query(sql, (days,))
        result = results[0] if results else {}
        
        total = result.get('total_feedback', 0) or 0
        helpful = result.get('helpful_count', 0) or 0
        
        helpful_pct = (helpful / total * 100) if total > 0 else 0
        
        return {
            "total_feedback": total,
            "helpful_percentage": round(helpful_pct, 2),
            "unhelpful_count": result.get('unhelpful_count', 0) or 0,
            "average_rating": round(result.get('avg_rating', 0) or 0, 2),
            "needs_improvement_count": result.get('needs_improvement_count', 0) or 0,
            "period_days": days
        }
    
    def get_low_rated_queries(self, rating_threshold: int = 2, limit: int = 20) -> list:
        """Get queries with low ratings that need improvement"""
        sql = """
            SELECT q.*, f.rating, f.comment
            FROM queries q
            JOIN feedback f ON q.id = f.query_id
            WHERE f.rating IS NOT NULL AND f.rating <= ?
            ORDER BY f.created_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (rating_threshold, limit))
    
    def mark_needs_improvement(self, feedback_id: str) -> bool:
        """Mark feedback as needing improvement"""
        sql = """
            UPDATE feedback 
            SET needs_improvement = TRUE
            WHERE id = ?
        """
        return self.db.execute_update(sql, (feedback_id,)) > 0
    
    def get_feedback_by_category(self, days: int = 30) -> list:
        """Get feedback metrics grouped by query category"""
        sql = """
            SELECT 
                q.category,
                COUNT(*) as total_queries,
                AVG(CAST(f.rating AS REAL)) as avg_rating,
                SUM(CASE WHEN f.helpful = 1 THEN 1 ELSE 0 END) as helpful_count
            FROM queries q
            LEFT JOIN feedback f ON q.id = f.query_id
            WHERE q.created_at >= datetime('now', '-' || ? || ' days')
            AND q.category IS NOT NULL
            GROUP BY q.category
            ORDER BY avg_rating ASC
        """
        return self.db.execute_query(sql, (days,))
    
    def get_recent_negative_feedback(self, limit: int = 10) -> list:
        """Get recent negative feedback"""
        sql = """
            SELECT f.*, q.question, u.username
            FROM feedback f
            JOIN queries q ON f.query_id = q.id
            JOIN users u ON f.user_id = u.id
            WHERE f.needs_improvement = TRUE
            OR (f.helpful = FALSE)
            ORDER BY f.created_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,))
