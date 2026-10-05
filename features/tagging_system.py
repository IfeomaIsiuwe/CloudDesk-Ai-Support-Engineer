"""
Tagging System - Auto-categorization and query tagging
"""
from database import DatabaseManager
from typing import List, Dict, Optional
import re


class TaggingSystem:
    """Automatic tagging and categorization of queries"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        "billing": ["payment", "invoice", "charge", "subscription", "bill", "cost", "price", "refund"],
        "account": ["password", "login", "account", "email", "username", "verification", "2fa"],
        "technical": ["error", "bug", "crash", "issue", "problem", "fix", "broken", "not working"],
        "general": ["question", "how", "what", "can", "help", "guide", "tutorial"],
        "critical": ["emergency", "urgent", "down", "offline", "cannot", "broken", "critical"]
    }
    
    SEVERITY_KEYWORDS = {
        "critical": ["emergency", "urgent", "critical", "down", "offline", "broken completely"],
        "high": ["major issue", "cannot use", "not working", "blocked"],
        "medium": ["issue", "problem", "error", "trouble"],
        "low": ["question", "how to", "information"]
    }
    
    def auto_categorize(self, question: str) -> tuple:
        """Auto-categorize a question"""
        question_lower = question.lower()
        
        category = self._find_category(question_lower)
        tags = self._extract_tags(question_lower)
        
        return category, tags
    
    def _find_category(self, text: str) -> Optional[str]:
        """Find best matching category"""
        max_score = 0
        best_category = None
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > max_score:
                max_score = score
                best_category = category
        
        return best_category if max_score > 0 else None
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        tags = []
        
        # Find severity
        for severity, keywords in self.SEVERITY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                tags.append(f"severity:{severity}")
                break
        
        # Extract specific product/feature mentions
        product_patterns = {
            "api": r"\bapi\b",
            "dashboard": r"\bdashboard\b",
            "mobile": r"\bmobile\b",
            "web": r"\bweb\b",
            "integration": r"\bintegration\b"
        }
        
        for tag, pattern in product_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                tags.append(f"product:{tag}")
        
        return tags
    
    def get_category_distribution(self, days: int = 30) -> Dict[str, int]:
        """Get query distribution by category"""
        sql = """
            SELECT category, COUNT(*) as count
            FROM queries
            WHERE category IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY category
            ORDER BY count DESC
        """
        results = self.db.execute_query(sql, (days,))
        return {row['category']: row['count'] for row in results}
    
    def get_tags_distribution(self, days: int = 30) -> Dict[str, int]:
        """Get distribution of tags"""
        sql = """
            SELECT tags, COUNT(*) as count
            FROM queries
            WHERE tags IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY tags
            ORDER BY count DESC
            LIMIT 20
        """
        import json
        results = self.db.execute_query(sql, (days,))
        distribution = {}
        
        for row in results:
            if row['tags']:
                try:
                    tags = json.loads(row['tags'])
                    for tag in tags:
                        distribution[tag] = distribution.get(tag, 0) + row['count']
                except:
                    pass
        
        return distribution
    
    def get_queries_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get all queries in a category"""
        sql = """
            SELECT * FROM queries
            WHERE category = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (category, limit))
    
    def get_queries_by_tag(self, tag: str, limit: int = 50) -> List[Dict]:
        """Get all queries with a specific tag"""
        sql = """
            SELECT * FROM queries
            WHERE tags LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (f'%{tag}%', limit))
    
    def get_high_priority_queries(self, limit: int = 20) -> List[Dict]:
        """Get high priority/critical queries"""
        sql = """
            SELECT * FROM queries
            WHERE tags LIKE '%critical%' OR tags LIKE '%high%'
            OR priority IN ('high', 'critical')
            ORDER BY created_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (limit,))
    
    def suggest_tags_for_query(self, question: str) -> List[str]:
        """Suggest tags for a new query"""
        _, auto_tags = self.auto_categorize(question)
        return auto_tags
    
    def get_category_health(self) -> Dict[str, Dict]:
        """Get health metrics by category"""
        sql = """
            SELECT 
                q.category,
                COUNT(*) as total_queries,
                SUM(CASE WHEN q.status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN q.status = 'escalated' THEN 1 ELSE 0 END) as escalated,
                AVG(CAST((SELECT confidence FROM query_responses 
                    WHERE query_id = q.id LIMIT 1) AS REAL)) as avg_confidence
            FROM queries q
            WHERE q.category IS NOT NULL
            GROUP BY q.category
        """
        results = self.db.execute_query(sql)
        
        health = {}
        for row in results:
            category = row['category']
            total = row['total_queries'] or 0
            resolved = row['resolved'] or 0
            escalated = row['escalated'] or 0
            
            health[category] = {
                "total_queries": total,
                "resolved_queries": resolved,
                "escalated_queries": escalated,
                "success_rate": round((resolved / total * 100) if total > 0 else 0, 2),
                "escalation_rate": round((escalated / total * 100) if total > 0 else 0, 2),
                "avg_confidence": round(row['avg_confidence'] or 0, 3)
            }
        
        return health
