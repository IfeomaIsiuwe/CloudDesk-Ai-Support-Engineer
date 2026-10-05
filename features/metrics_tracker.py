"""
Metrics Tracker - Tracks system-wide statistics and analytics
"""
from database import DatabaseManager
from typing import Dict, Any
from datetime import datetime


class MetricsTracker:
    """Tracks and aggregates system metrics"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        metrics = self.db.get_metrics_summary(days)
        
        # Calculate percentages
        total_queries = metrics['total_queries']
        if total_queries > 0:
            resolved_pct = (metrics['resolved_queries'] / total_queries) * 100
            escalated_pct = (metrics['escalated_queries'] / total_queries) * 100
        else:
            resolved_pct = 0
            escalated_pct = 0
        
        avg_rating = self.db.get_avg_rating(days)
        
        return {
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat(),
            # Query metrics
            "total_queries": metrics['total_queries'],
            "resolved_queries": metrics['resolved_queries'],
            "escalated_queries": metrics['escalated_queries'],
            "resolved_percentage": round(resolved_pct, 2),
            "escalated_percentage": round(escalated_pct, 2),
            # Quality metrics
            "avg_confidence": round(metrics['avg_confidence'], 3),
            "avg_response_time_ms": round(metrics['avg_response_time_ms'], 2),
            "avg_rating": round(avg_rating, 2),
            # User metrics
            "unique_users": metrics['unique_users'],
            # Performance indicators
            "health_status": self._calculate_health(metrics, avg_rating)
        }
    
    def _calculate_health(self, metrics: Dict, avg_rating: float) -> str:
        """Calculate overall system health"""
        health_score = 0
        
        # Confidence scoring
        if metrics['avg_confidence'] >= 0.7:
            health_score += 30
        elif metrics['avg_confidence'] >= 0.5:
            health_score += 20
        else:
            health_score += 10
        
        # Escalation rate
        total = metrics['total_queries']
        if total > 0:
            escalation_rate = metrics['escalated_queries'] / total
            if escalation_rate <= 0.2:
                health_score += 30
            elif escalation_rate <= 0.4:
                health_score += 20
            else:
                health_score += 10
        else:
            health_score += 20
        
        # Rating
        if avg_rating >= 4.0:
            health_score += 20
        elif avg_rating >= 3.0:
            health_score += 15
        else:
            health_score += 10
        
        # Response time
        if metrics['avg_response_time_ms'] < 1000:
            health_score += 20
        elif metrics['avg_response_time_ms'] < 2000:
            health_score += 10
        
        if health_score >= 80:
            return "Excellent"
        elif health_score >= 60:
            return "Good"
        elif health_score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def get_trend_data(self, days: int = 30) -> Dict[str, Any]:
        """Get trending data"""
        top_queries = self.db.get_top_queries(limit=10)
        
        return {
            "top_queries": top_queries,
            "trending_categories": self._get_trending_categories(),
            "escalation_trends": self._get_escalation_trends(days)
        }
    
    def _get_trending_categories(self) -> list:
        """Get trending query categories"""
        sql = """
            SELECT category, COUNT(*) as count
            FROM queries
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        """
        return self.db.execute_query(sql)
    
    def _get_escalation_trends(self, days: int) -> Dict:
        """Get escalation trends"""
        sql = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) as escalated
            FROM queries
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        return self.db.execute_query(sql, (days,))
    
    def log_performance_metric(self, metric_name: str, value: float, category: str = "system"):
        """Log a performance metric"""
        self.db.insert_performance_metric(metric_name, value, category)
    
    def get_performance_metrics(self, metric_name: str, hours: int = 24) -> list:
        """Get performance metrics for a metric name"""
        sql = """
            SELECT * FROM performance_metrics
            WHERE metric_name = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        """
        return self.db.execute_query(sql, (metric_name, hours))
