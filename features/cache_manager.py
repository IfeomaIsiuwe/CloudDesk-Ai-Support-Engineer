"""
Cache Manager - Query result caching and optimization
"""
from database import DatabaseManager
from typing import Optional, Dict, Any
import hashlib
import json


class CacheManager:
    """Manages query result caching"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.sha256(query.lower().encode()).hexdigest()
    
    def get_cached_result(self, query: str) -> Optional[Dict]:
        """Get cached result if available"""
        cache_key = self.get_cache_key(query)
        return self.db.get_cached_response(cache_key)
    
    def cache_result(self, query: str, result: Dict, ttl_seconds: int = 86400):
        """Cache a query result"""
        cache_key = self.get_cache_key(query)
        self.db.cache_response(cache_key, result, ttl_seconds)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        sql = """
            SELECT 
                COUNT(*) as total_cached,
                SUM(hit_count) as total_hits,
                AVG(hit_count) as avg_hits,
                MAX(hit_count) as max_hits
            FROM cache_entries
            WHERE expires_at > CURRENT_TIMESTAMP
        """
        results = self.db.execute_query(sql)
        result = results[0] if results else {}
        
        return {
            "total_cached_queries": result.get('total_cached', 0) or 0,
            "total_cache_hits": result.get('total_hits', 0) or 0,
            "avg_hits_per_query": round(result.get('avg_hits', 0) or 0, 2),
            "most_reused_cache_hits": result.get('max_hits', 0) or 0
        }
    
    def get_most_cached_queries(self, limit: int = 20) -> list:
        """Get most frequently cached queries"""
        sql = """
            SELECT query_hash, hit_count, created_at, expires_at
            FROM cache_entries
            WHERE expires_at > CURRENT_TIMESTAMP
            ORDER BY hit_count DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,))
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        sql = "DELETE FROM cache_entries WHERE expires_at <= CURRENT_TIMESTAMP"
        return self.db.execute_update(sql)
    
    def clear_cache_by_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        sql = "DELETE FROM cache_entries WHERE query_hash LIKE ?"
        return self.db.execute_update(sql, (f"%{pattern}%",))
    
    def calculate_cache_efficiency(self) -> Dict[str, Any]:
        """Calculate cache efficiency"""
        total_queries_sql = """
            SELECT COUNT(*) as total FROM queries WHERE created_at >= datetime('now', '-1 day')
        """
        cached_hits_sql = """
            SELECT SUM(hit_count) as hits FROM cache_entries
        """
        
        total = self.db.execute_query(total_queries_sql)[0].get('total', 0) or 0
        hits = self.db.execute_query(cached_hits_sql)[0].get('hits', 0) or 0
        
        efficiency = (hits / (total + hits) * 100) if (total + hits) > 0 else 0
        
        return {
            "total_queries_24h": total,
            "total_cache_hits_24h": hits,
            "cache_efficiency_percentage": round(efficiency, 2)
        }
