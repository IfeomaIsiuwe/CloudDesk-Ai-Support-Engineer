"""
Search Analytics - Track search patterns and insights
"""
from database import DatabaseManager
from typing import List, Dict, Optional, Any


class SearchAnalytics:
    """Analyzes search patterns and provides insights"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def record_search(self, query: str, category: Optional[str] = None, 
                     success: bool = True, escalated: bool = False):
        """Record a search query"""
        self.db.update_search_analytic(query, category, success, escalated)
    
    def get_top_queries(self, limit: int = 20) -> List[Dict]:
        """Get most searched queries"""
        return self.db.get_top_queries(limit)
    
    def get_search_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get search trends over time"""
        sql = """
            SELECT 
                strftime('%Y-%m-%d', last_searched) as date,
                COUNT(*) as search_count,
                SUM(search_count) as total_searches
            FROM search_analytics
            WHERE last_searched >= datetime('now', '-' || ? || ' days')
            GROUP BY date
            ORDER BY date DESC
        """
        trends = self.db.execute_query(sql, (days,))
        
        return {
            "daily_trends": trends,
            "period_days": days
        }
    
    def get_search_by_category(self) -> Dict[str, int]:
        """Get search distribution by category"""
        sql = """
            SELECT category, SUM(search_count) as total
            FROM search_analytics
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY total DESC
        """
        results = self.db.execute_query(sql)
        return {row['category']: row['total'] for row in results}
    
    def get_low_success_queries(self, limit: int = 20) -> List[Dict]:
        """Get queries with low success rate"""
        sql = """
            SELECT * FROM search_analytics
            WHERE success_rate < 0.5
            ORDER BY search_count DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,))
    
    def get_high_escalation_queries(self, threshold: float = 0.3, limit: int = 20) -> List[Dict]:
        """Get queries that frequently escalate"""
        sql = """
            SELECT * FROM search_analytics
            WHERE escalation_rate > ?
            ORDER BY escalation_rate DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (threshold, limit))
    
    def get_search_analytics_summary(self) -> Dict[str, Any]:
        """Get overall search analytics summary"""
        sql = """
            SELECT 
                COUNT(*) as total_unique_queries,
                SUM(search_count) as total_searches,
                AVG(success_rate) as avg_success_rate,
                AVG(escalation_rate) as avg_escalation_rate,
                AVG(avg_response_time_ms) as avg_response_time
            FROM search_analytics
        """
        results = self.db.execute_query(sql)
        result = results[0] if results else {}
        
        return {
            "total_unique_queries": result.get('total_unique_queries', 0) or 0,
            "total_searches": result.get('total_searches', 0) or 0,
            "avg_success_rate": round(result.get('avg_success_rate', 0) or 0, 3),
            "avg_escalation_rate": round(result.get('avg_escalation_rate', 0) or 0, 3),
            "avg_response_time_ms": round(result.get('avg_response_time', 0) or 0, 2)
        }
    
    def get_knowledge_gap_analysis(self) -> List[Dict]:
        """Identify knowledge gaps - queries that frequently escalate"""
        sql = """
            SELECT query, category, search_count, escalation_rate
            FROM search_analytics
            WHERE escalation_rate > 0.3
            AND search_count >= 5
            ORDER BY (search_count * escalation_rate) DESC
            LIMIT 20
        """
        return self.db.execute_query(sql)
    
    def get_improvement_opportunities(self) -> List[Dict]:
        """Get queries that could be improved"""
        sql = """
            SELECT 
                query,
                category,
                search_count,
                success_rate,
                avg_response_time_ms
            FROM search_analytics
            WHERE success_rate < 0.7 AND search_count >= 3
            ORDER BY search_count DESC
            LIMIT 20
        """
        return self.db.execute_query(sql)
    
    def get_query_effectiveness_score(self, query: str) -> Dict[str, Any]:
        """Get effectiveness score for a query"""
        sql = """
            SELECT * FROM search_analytics WHERE query = ? LIMIT 1
        """
        results = self.db.execute_query(sql, (query,))
        
        if not results:
            return {"query": query, "status": "not_found"}
        
        result = results[0]
        
        # Calculate effectiveness score (0-100)
        success_component = result['success_rate'] * 40
        response_time_component = max(0, 20 - (result['avg_response_time_ms'] / 100))
        volume_component = min(20, result['search_count'] / 10)
        
        effectiveness_score = success_component + response_time_component + volume_component
        
        return {
            "query": query,
            "search_count": result['search_count'],
            "success_rate": round(result['success_rate'], 3),
            "escalation_rate": round(result['escalation_rate'], 3),
            "avg_response_time_ms": round(result['avg_response_time_ms'], 2),
            "effectiveness_score": round(effectiveness_score, 2)
        }
