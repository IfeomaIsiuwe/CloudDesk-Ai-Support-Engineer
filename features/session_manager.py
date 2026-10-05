"""
Session Manager - Manages user sessions and conversation history
"""
from database import DatabaseManager
from typing import Optional, List, Dict, Any


class SessionManager:
    """Manages user sessions and conversation context"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_session(self, user_id: str) -> str:
        """Create a new user session"""
        session_id = self.db.insert_session(user_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details"""
        return self.db.get_session(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End a session"""
        return self.db.end_session(session_id) > 0
    
    def get_session_conversation(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        sql = """
            SELECT q.id, q.question, q.status, q.created_at,
                   qr.answer, qr.confidence
            FROM queries q
            LEFT JOIN query_responses qr ON q.id = qr.query_id
            WHERE q.session_id = ?
            ORDER BY q.created_at ASC
        """
        return self.db.execute_query(sql, (session_id,))
    
    def add_query_to_session(self, session_id: str, user_id: str, question: str) -> str:
        """Add a query to session"""
        query_id = self.db.insert_query(user_id, session_id, question)
        return query_id
    
    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's recent sessions"""
        sql = """
            SELECT * FROM sessions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        return self.db.execute_query(sql, (user_id, limit))
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        conversation = self.get_session_conversation(session_id)
        
        resolved = sum(1 for q in conversation if q['status'] == 'resolved')
        escalated = sum(1 for q in conversation if q['status'] == 'escalated')
        
        avg_confidence = 0
        confidences = [float(q['confidence']) for q in conversation if q['confidence']]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
        
        return {
            "session_id": session_id,
            "user_id": session['user_id'],
            "total_queries": session['query_count'],
            "resolved_queries": resolved,
            "escalated_queries": escalated,
            "avg_confidence": round(avg_confidence, 3),
            "total_response_time_ms": session['total_response_time_ms'],
            "created_at": session['created_at'],
            "ended_at": session['ended_at'],
            "duration_minutes": self._calculate_duration(session)
        }
    
    def _calculate_duration(self, session: Dict) -> float:
        """Calculate session duration in minutes"""
        if not session.get('ended_at'):
            return 0
        
        from datetime import datetime
        try:
            created = datetime.fromisoformat(session['created_at'])
            ended = datetime.fromisoformat(session['ended_at'])
            duration = (ended - created).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        sql = """
            SELECT s.*, u.username, u.email
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.ended_at IS NULL
            ORDER BY s.created_at DESC
        """
        return self.db.execute_query(sql)
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context from previous queries in session for current query"""
        conversation = self.get_session_conversation(session_id)
        
        # Extract relevant context
        categories_mentioned = list(set(
            q['category'] for q in conversation 
            if q['category'] is not None
        ))
        
        previous_topics = [q['question'] for q in conversation[:-1]]
        
        return {
            "previous_queries": len(conversation),
            "categories_mentioned": categories_mentioned,
            "previous_topics": previous_topics[-5:],  # Last 5
            "user_context": self._extract_user_preferences(session_id)
        }
    
    def _extract_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Extract user preferences from session"""
        sql = """
            SELECT 
                q.category,
                COUNT(*) as frequency
            FROM queries q
            WHERE q.session_id = ?
            GROUP BY q.category
            ORDER BY frequency DESC
        """
        categories = self.db.execute_query(sql, (session_id,))
        
        return {
            "preferred_categories": [c['category'] for c in categories],
            "category_distribution": categories
        }
    
    def update_session_stats(self, session_id: str):
        """Update session statistics based on queries"""
        session = self.get_session(session_id)
        if not session:
            return
        
        sql = """
            SELECT 
                COUNT(*) as query_count,
                SUM(CASE WHEN q.status = 'escalated' THEN 1 ELSE 0 END) as escalation_count,
                SUM(COALESCE(qr.response_time_ms, 0)) as total_response_time
            FROM queries q
            LEFT JOIN query_responses qr ON q.id = qr.query_id
            WHERE q.session_id = ?
        """
        results = self.db.execute_query(sql, (session_id,))
        result = results[0] if results else {}
        
        self.db.update_session_stats(
            session_id,
            result.get('query_count', 0) or 0,
            result.get('escalation_count', 0) or 0,
            result.get('total_response_time', 0) or 0
        )
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a user across all sessions"""
        sql = """
            SELECT 
                COUNT(DISTINCT s.id) as total_sessions,
                SUM(s.query_count) as total_queries,
                SUM(s.escalation_count) as total_escalations,
                AVG(s.query_count) as avg_queries_per_session,
                COUNT(CASE WHEN s.ended_at IS NULL THEN 1 END) as active_sessions
            FROM sessions s
            WHERE s.user_id = ?
        """
        results = self.db.execute_query(sql, (user_id,))
        result = results[0] if results else {}
        
        return {
            "total_sessions": result.get('total_sessions', 0) or 0,
            "total_queries": result.get('total_queries', 0) or 0,
            "total_escalations": result.get('total_escalations', 0) or 0,
            "avg_queries_per_session": round(result.get('avg_queries_per_session', 0) or 0, 2),
            "active_sessions": result.get('active_sessions', 0) or 0
        }
