"""
Knowledge Updater - Learn from Tier 2 responses and improve over time
"""
from database import DatabaseManager
from typing import Optional, List, Dict, Any
import hashlib
import json


class KnowledgeUpdater:
    """Manages learning from Tier 2 responses"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def save_tier2_response(self, original_query_id: str, tier2_response: str,
                           category: str, tags: List[str] = None) -> str:
        """Save response from Tier 2 as learned knowledge"""
        if tags is None:
            tags = []
        
        learned_id = self.db.insert_learned_response(
            original_query_id, tier2_response, category, tags
        )
        
        # Log this action
        self.db.insert_audit_log(
            "system", "create_learned_response", "learned_response", 
            learned_id, None, tier2_response
        )
        
        return learned_id
    
    def get_similar_learned_response(self, category: str, confidence_threshold: float = 0.6) -> Optional[Dict]:
        """Get learned response if similar question was previously escalated"""
        learned_responses = self.db.get_learned_responses_by_category(category)
        
        if learned_responses:
            best_match = learned_responses[0]
            if best_match['confidence_threshold'] <= confidence_threshold:
                self.db.increment_learned_response_usage(best_match['id'])
                return best_match
        
        return None
    
    def get_learned_responses_by_category(self, category: str) -> List[Dict]:
        """Get all learned responses for a category"""
        return self.db.get_learned_responses_by_category(category)
    
    def deactivate_learned_response(self, learned_id: str) -> bool:
        """Deactivate a learned response if it's not helpful"""
        sql = """
            UPDATE learned_responses 
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_update(sql, (learned_id,)) > 0
    
    def update_learned_response_confidence(self, learned_id: str, new_confidence: float) -> bool:
        """Update confidence threshold for a learned response"""
        sql = """
            UPDATE learned_responses 
            SET confidence_threshold = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_update(sql, (new_confidence, learned_id)) > 0
    
    def get_top_learned_responses(self, limit: int = 20) -> list:
        """Get most reused learned responses"""
        sql = """
            SELECT * FROM learned_responses
            WHERE is_active = TRUE
            ORDER BY times_reused DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,))
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics on the learning system"""
        sql = """
            SELECT 
                COUNT(*) as total_learned,
                SUM(times_reused) as total_reuses,
                AVG(times_reused) as avg_reuses,
                MAX(times_reused) as max_reuses,
                COUNT(DISTINCT category) as categories
            FROM learned_responses
            WHERE is_active = TRUE
        """
        results = self.db.execute_query(sql)
        result = results[0] if results else {}
        
        return {
            "total_learned_responses": result.get('total_learned', 0) or 0,
            "total_reuses": result.get('total_reuses', 0) or 0,
            "avg_reuses_per_response": round(result.get('avg_reuses', 0) or 0, 2),
            "max_reuses": result.get('max_reuses', 0) or 0,
            "categories_with_learning": result.get('categories', 0) or 0
        }
    
    def calculate_learning_effectiveness(self, days: int = 30) -> Dict[str, Any]:
        """Calculate how effective the learning system is"""
        # Get queries that were escalated but could have been answered by learned responses
        sql = """
            SELECT 
                lr.id,
                COUNT(DISTINCT q.id) as potential_matches
            FROM learned_responses lr
            LEFT JOIN queries q ON (
                q.category = lr.category 
                AND q.status = 'escalated'
                AND q.created_at >= datetime('now', '-' || ? || ' days')
            )
            WHERE lr.is_active = TRUE
            GROUP BY lr.id
        """
        results = self.db.execute_query(sql, (days,))
        
        total_potential = sum(r.get('potential_matches', 0) or 0 for r in results)
        total_reused = sum(r.get('times_reused', 0) or 0 for r in results)
        
        return {
            "potential_matches_avoided": total_potential,
            "actual_reuses": total_reused,
            "period_days": days,
            "effectiveness_score": round((total_reused / total_potential * 100) if total_potential > 0 else 0, 2)
        }
    
    def get_category_learning_coverage(self) -> Dict[str, Any]:
        """Get coverage of learning by category"""
        sql = """
            SELECT 
                lr.category,
                COUNT(DISTINCT lr.id) as learned_responses,
                SUM(lr.times_reused) as total_reuses,
                COUNT(DISTINCT q.id) as related_queries
            FROM learned_responses lr
            LEFT JOIN queries q ON q.category = lr.category
            WHERE lr.is_active = TRUE
            GROUP BY lr.category
            ORDER BY learned_responses DESC
        """
        return self.db.execute_query(sql)
    
    def suggest_new_learning_areas(self, days: int = 30, min_escalations: int = 3) -> list:
        """Suggest categories that should have more learned responses"""
        sql = """
            SELECT 
                q.category,
                COUNT(*) as escalation_count,
                COUNT(DISTINCT lr.id) as learned_responses
            FROM queries q
            LEFT JOIN learned_responses lr ON q.category = lr.category
            WHERE q.status = 'escalated'
            AND q.created_at >= datetime('now', '-' || ? || ' days')
            AND q.category IS NOT NULL
            GROUP BY q.category
            HAVING escalation_count >= ?
            ORDER BY escalation_count DESC
        """
        return self.db.execute_query(sql, (days, min_escalations))
