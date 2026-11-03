"""
REST API for CloudDesk AI Support System
"""
from flask import Flask, request, jsonify
from functools import wraps
from database import DatabaseManager
from features import *
import os
import json


app = Flask(__name__)
db = DatabaseManager()

# Initialize feature managers
metrics_tracker = MetricsTracker(db)
feedback_system = FeedbackSystem(db)
knowledge_updater = KnowledgeUpdater(db)
session_manager = SessionManager(db)
escalation_rules = EscalationRules(db)
cache_manager = CacheManager(db)
tagging_system = TaggingSystem(db)
notification_handler = NotificationHandler(db)
audit_logger = AuditLogger(db)
search_analytics = SearchAnalytics(db)
user_manager = UserManager(db)


def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401
        
        user = user_manager.validate_api_key(api_key)
        if not user:
            return jsonify({"error": "Invalid API key"}), 401
        
        request.user = user
        return f(*args, **kwargs)
    return decorated_function


# ==================== Health & Status ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "CloudDesk AI Support"}), 200


# ==================== Metrics Endpoints ====================

@app.route('/api/metrics/summary', methods=['GET'])
@require_api_key
def get_metrics_summary():
    """Get metrics summary"""
    days = request.args.get('days', 30, type=int)
    summary = metrics_tracker.get_summary(days)
    return jsonify(summary), 200


@app.route('/api/metrics/trends', methods=['GET'])
@require_api_key
def get_metrics_trends():
    """Get metrics trends"""
    days = request.args.get('days', 30, type=int)
    trends = metrics_tracker.get_trend_data(days)
    return jsonify(trends), 200


# ==================== Query Endpoints ====================

@app.route('/api/queries', methods=['POST'])
@require_api_key
def create_query():
    """Create a new query"""
    data = request.get_json()
    
    # Get or create session
    session_id = data.get('session_id')
    if not session_id:
        session_id = session_manager.create_session(request.user['id'])
    
    question = data.get('question')
    if not question:
        return jsonify({"error": "Question required"}), 400
    
    query_id = session_manager.add_query_to_session(
        session_id, request.user['id'], question
    )
    
    # Auto-categorize
    category, tags = tagging_system.auto_categorize(question)
    db.update_query_category(query_id, category, tags)
    
    return jsonify({
        "query_id": query_id,
        "session_id": session_id,
        "category": category,
        "tags": tags
    }), 201


@app.route('/api/queries/<query_id>', methods=['GET'])
@require_api_key
def get_query(query_id):
    """Get query details"""
    query = db.get_query(query_id)
    if not query:
        return jsonify({"error": "Query not found"}), 404
    
    response = db.get_query_response(query_id)
    feedback = db.get_feedback(query_id)
    
    return jsonify({
        "query": query,
        "response": response,
        "feedback": feedback
    }), 200


# ==================== Feedback Endpoints ====================

@app.route('/api/feedback', methods=['POST'])
@require_api_key
def submit_feedback():
    """Submit feedback on a response"""
    data = request.get_json()
    
    feedback_id = feedback_system.submit_feedback(
        data.get('query_id'),
        data.get('response_id'),
        request.user['id'],
        data.get('rating'),
        data.get('helpful', False),
        data.get('comment')
    )
    
    return jsonify({"feedback_id": feedback_id}), 201


@app.route('/api/feedback/summary', methods=['GET'])
@require_api_key
def get_feedback_summary():
    """Get feedback summary"""
    days = request.args.get('days', 30, type=int)
    summary = feedback_system.get_feedback_summary(days)
    return jsonify(summary), 200


# ==================== Escalation Endpoints ====================

@app.route('/api/escalations', methods=['GET'])
@require_api_key
def get_escalations():
    """Get escalation queue"""
    priority = request.args.get('priority')
    limit = request.args.get('limit', 50, type=int)
    
    escalations = escalation_rules.get_escalation_queue(priority, limit)
    return jsonify(escalations), 200


@app.route('/api/escalations/<ticket_id>/resolve', methods=['POST'])
@require_api_key
def resolve_escalation(ticket_id):
    """Resolve an escalation"""
    if not user_manager.is_tier2_support(request.user['id']):
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    escalation_rules.resolve_escalation(
        ticket_id,
        data.get('response'),
        data.get('notes')
    )
    
    return jsonify({"status": "resolved"}), 200


# ==================== Knowledge Endpoints ====================

@app.route('/api/knowledge/<category>', methods=['GET'])
@require_api_key
def get_learned_responses(category):
    """Get learned responses for category"""
    responses = knowledge_updater.get_learned_responses_by_category(category)
    return jsonify(responses), 200


@app.route('/api/knowledge/stats', methods=['GET'])
@require_api_key
def get_knowledge_stats():
    """Get knowledge system statistics"""
    stats = knowledge_updater.get_learning_statistics()
    effectiveness = knowledge_updater.calculate_learning_effectiveness()
    
    return jsonify({
        "statistics": stats,
        "effectiveness": effectiveness
    }), 200


# ==================== Search Analytics Endpoints ====================

@app.route('/api/analytics/top-queries', methods=['GET'])
@require_api_key
def get_top_queries():
    """Get top searched queries"""
    limit = request.args.get('limit', 20, type=int)
    queries = search_analytics.get_top_queries(limit)
    return jsonify(queries), 200


@app.route('/api/analytics/search-summary', methods=['GET'])
@require_api_key
def get_search_summary():
    """Get search analytics summary"""
    summary = search_analytics.get_search_analytics_summary()
    return jsonify(summary), 200


@app.route('/api/analytics/knowledge-gaps', methods=['GET'])
@require_api_key
def get_knowledge_gaps():
    """Get knowledge gaps analysis"""
    gaps = search_analytics.get_knowledge_gap_analysis()
    return jsonify(gaps), 200


# ==================== User Endpoints ====================

@app.route('/api/users/profile', methods=['GET'])
@require_api_key
def get_user_profile():
    """Get user profile"""
    user = user_manager.get_user(request.user['id'])
    stats = user_manager.get_user_statistics(request.user['id'])
    
    return jsonify({
        "user": user,
        "statistics": stats
    }), 200


@app.route('/api/users/sessions', methods=['GET'])
@require_api_key
def get_user_sessions():
    """Get user sessions"""
    limit = request.args.get('limit', 20, type=int)
    sessions = session_manager.get_user_sessions(request.user['id'], limit)
    return jsonify(sessions), 200


# ==================== Notification Endpoints ====================

@app.route('/api/notifications/unread', methods=['GET'])
@require_api_key
def get_unread_notifications():
    """Get unread notifications"""
    notifications = notification_handler.get_unread_notifications(request.user['id'])
    return jsonify(notifications), 200


@app.route('/api/notifications/<notif_id>/read', methods=['POST'])
@require_api_key
def mark_notification_read(notif_id):
    """Mark notification as read"""
    notification_handler.mark_notification_read(notif_id)
    return jsonify({"status": "read"}), 200


# ==================== Cache Endpoints ====================

@app.route('/api/cache/stats', methods=['GET'])
@require_api_key
def get_cache_stats():
    """Get cache statistics"""
    stats = cache_manager.get_cache_stats()
    efficiency = cache_manager.calculate_cache_efficiency()
    
    return jsonify({
        "statistics": stats,
        "efficiency": efficiency
    }), 200


@app.route('/api/cache/clear', methods=['POST'])
@require_api_key
def clear_cache():
    """Clear expired cache"""
    if not user_manager.is_admin(request.user['id']):
        return jsonify({"error": "Unauthorized"}), 403
    
    count = cache_manager.clear_expired_cache()
    return jsonify({"cleared_entries": count}), 200


# ==================== Admin Endpoints ====================

@app.route('/api/admin/audit-logs', methods=['GET'])
@require_api_key
def get_audit_logs():
    """Get audit logs"""
    if not user_manager.is_admin(request.user['id']):
        return jsonify({"error": "Unauthorized"}), 403
    
    resource_id = request.args.get('resource_id')
    limit = request.args.get('limit', 100, type=int)
    
    logs = audit_logger.get_audit_trail(resource_id, limit) if resource_id else audit_logger.get_audit_summary()
    return jsonify(logs), 200


@app.route('/api/admin/compliance-report', methods=['GET'])
@require_api_key
def get_compliance_report():
    """Get compliance report"""
    if not user_manager.is_admin(request.user['id']):
        return jsonify({"error": "Unauthorized"}), 403
    
    days = request.args.get('days', 90, type=int)
    report = audit_logger.compliance_report(days)
    return jsonify(report), 200


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
