"""
User Manager - Manage user profiles and permissions
"""
from database import DatabaseManager
from typing import Optional, List, Dict, Any
import uuid
import hashlib


class UserManager:
    """Manages user profiles and access control"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_user(self, username: str, email: str, role: str = "customer") -> str:
        """Create new user"""
        user_id = self.db.insert_user(username, email, role)
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.db.get_user(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return self.db.get_user_by_email(email)
    
    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update user role"""
        sql = """
            UPDATE users
            SET role = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_update(sql, (new_role, user_id)) > 0
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        sql = """
            UPDATE users
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_update(sql, (user_id,)) > 0
    
    def activate_user(self, user_id: str) -> bool:
        """Activate user account"""
        sql = """
            UPDATE users
            SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        return self.db.execute_update(sql, (user_id,)) > 0
    
    def get_all_users(self, role: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get all users, optionally filtered by role"""
        if role:
            sql = """
                SELECT * FROM users
                WHERE role = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            return self.db.execute_query(sql, (role, limit))
        else:
            sql = """
                SELECT * FROM users
                ORDER BY created_at DESC
                LIMIT ?
            """
            return self.db.execute_query(sql, (limit,))
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        sql = """
            SELECT 
                COUNT(DISTINCT s.id) as total_sessions,
                SUM(s.query_count) as total_queries,
                SUM(s.escalation_count) as total_escalations,
                AVG(CAST((SELECT confidence FROM query_responses 
                    WHERE query_id = q.id LIMIT 1) AS REAL)) as avg_confidence
            FROM sessions s
            LEFT JOIN queries q ON q.session_id = s.id
            WHERE s.user_id = ?
        """
        results = self.db.execute_query(sql, (user_id,))
        result = results[0] if results else {}
        
        return {
            "total_sessions": result.get('total_sessions', 0) or 0,
            "total_queries": result.get('total_queries', 0) or 0,
            "total_escalations": result.get('total_escalations', 0) or 0,
            "avg_confidence": round(result.get('avg_confidence', 0) or 0, 3)
        }
    
    def get_active_users(self, days: int = 30) -> List[Dict]:
        """Get users active in last N days"""
        sql = """
            SELECT DISTINCT u.*
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY u.created_at DESC
        """
        return self.db.execute_query(sql, (days,))
    
    def generate_api_key(self, user_id: str, key_name: str) -> str:
        """Generate API key for user"""
        api_key = str(uuid.uuid4())
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        key_id = str(uuid.uuid4())
        sql = """
            INSERT INTO api_keys (id, user_id, name, key_hash)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_update(sql, (key_id, user_id, key_name, key_hash))
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        sql = """
            SELECT * FROM api_keys
            WHERE key_hash = ? AND is_active = TRUE
            LIMIT 1
        """
        results = self.db.execute_query(sql, (key_hash,))
        return results[0] if results else None
    
    def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user role"""
        user = self.get_user(user_id)
        return user['role'] if user else None
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        return self.get_user_role(user_id) == "admin"
    
    def is_tier2_support(self, user_id: str) -> bool:
        """Check if user is tier 2 support"""
        return self.get_user_role(user_id) == "tier2"
    
    def get_user_organization(self, user_id: str) -> Optional[str]:
        """Get user's organization"""
        user = self.get_user(user_id)
        return user['organization'] if user else None
    
    def get_organization_users(self, organization: str) -> List[Dict]:
        """Get all users in an organization"""
        sql = """
            SELECT * FROM users
            WHERE organization = ?
            ORDER BY username
        """
        return self.db.execute_query(sql, (organization,))
    
    def get_user_preference(self, user_id: str, preference_key: str) -> Optional[str]:
        """Get user preference"""
        user = self.get_user(user_id)
        if user and user.get('metadata'):
            import json
            try:
                metadata = json.loads(user['metadata'])
                return metadata.get(preference_key)
            except:
                return None
        return None
