"""
Admin Dashboard for CloudDesk
Run with: streamlit run dashboards/admin_dashboard.py
"""
import sys
sys.path.insert(0, '/home/whizic/UK/AMDARI/CloudDesk')

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import DatabaseManager
from features import *

# Page config
st.set_page_config(
    page_title="CloudDesk Admin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
db = DatabaseManager()
metrics_tracker = MetricsTracker(db)
feedback_system = FeedbackSystem(db)
knowledge_updater = KnowledgeUpdater(db)
escalation_rules = EscalationRules(db)
audit_logger = AuditLogger(db)
search_analytics = SearchAnalytics(db)
user_manager = UserManager(db)


# Custom CSS
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
}
.stat-number {
    font-size: 2rem;
    font-weight: bold;
}
.stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔧 Admin Dashboard")
page = st.sidebar.radio("Select Page", [
    "Overview",
    "Metrics & Analytics",
    "Escalations",
    "Knowledge Base",
    "User Management",
    "Audit Logs",
    "System Health"
])

# ==================== OVERVIEW ====================
if page == "Overview":
    st.title("📊 CloudDesk Admin Overview")
    
    days = st.sidebar.slider("Select period (days)", 1, 90, 30)
    
    # Metrics
    metrics = metrics_tracker.get_summary(days)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Queries", metrics['total_queries'], 
                 f"{metrics['resolved_percentage']:.1f}% Resolved")
    
    with col2:
        st.metric("Escalated", metrics['escalated_queries'],
                 f"{metrics['escalated_percentage']:.1f}%")
    
    with col3:
        st.metric("Avg Confidence", f"{metrics['avg_confidence']:.1%}",
                 metrics['health_status'])
    
    with col4:
        st.metric("Response Time", f"{metrics['avg_response_time_ms']:.0f}ms")
    
    with col5:
        st.metric("Active Users", metrics['unique_users'])
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Query Status Distribution")
        data = {
            "Status": ["Resolved", "Escalated"],
            "Count": [metrics['resolved_queries'], metrics['escalated_queries']]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index("Status"))
    
    with col2:
        st.subheader("System Health")
        health_map = {
            "Excellent": "🟢",
            "Good": "🟡",
            "Fair": "🟠",
            "Poor": "🔴"
        }
        st.write(f"### {health_map.get(metrics['health_status'], '❓')} {metrics['health_status']}")
        st.write(f"Average Rating: ⭐ {metrics.get('avg_rating', 0):.2f}/5")


# ==================== METRICS & ANALYTICS ====================
elif page == "Metrics & Analytics":
    st.title("📈 Metrics & Analytics")
    
    days = st.sidebar.slider("Select period (days)", 1, 90, 30)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Query Metrics")
        metrics = metrics_tracker.get_summary(days)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total Queries", metrics['total_queries'])
            st.metric("Resolved", metrics['resolved_queries'])
        with col_b:
            st.metric("Escalated", metrics['escalated_queries'])
            st.metric("Avg Confidence", f"{metrics['avg_confidence']:.1%}")
    
    with col2:
        st.subheader("Search Analytics")
        search_summary = search_analytics.get_search_analytics_summary()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Unique Queries", search_summary['total_unique_queries'])
            st.metric("Total Searches", search_summary['total_searches'])
        with col_b:
            st.metric("Avg Success Rate", f"{search_summary['avg_success_rate']:.1%}")
            st.metric("Avg Response Time", f"{search_summary['avg_response_time_ms']:.0f}ms")
    
    st.divider()
    
    # Trend data
    trends = metrics_tracker.get_trend_data(days)
    
    if trends['escalation_trends']:
        st.subheader("Escalation Trends")
        trend_df = pd.DataFrame(trends['escalation_trends'])
        st.line_chart(trend_df.set_index('date')[['escalated']])
    
    # Top queries
    st.subheader("Top Searched Queries")
    top_queries = search_analytics.get_top_queries(10)
    if top_queries:
        df = pd.DataFrame(top_queries)
        st.dataframe(df[['query', 'search_count', 'success_rate']], use_container_width=True)


# ==================== ESCALATIONS ====================
elif page == "Escalations":
    st.title("🚨 Escalation Management")
    
    col1, col2, col3, col4 = st.columns(4)
    
    escalation_stats = escalation_rules.get_escalation_statistics()
    
    with col1:
        st.metric("Total Escalations", escalation_stats['total_escalations'])
    with col2:
        st.metric("Open Tickets", escalation_stats['open_escalations'])
    with col3:
        st.metric("Resolved", escalation_stats['resolved_escalations'])
    with col4:
        st.metric("Avg Response Time", f"{escalation_stats['avg_response_time_minutes']:.0f} min")
    
    st.divider()
    
    # Open escalations
    st.subheader("Open Escalation Tickets")
    open_tickets = escalation_rules.get_escalation_queue(limit=20)
    
    if open_tickets:
        df = pd.DataFrame(open_tickets)
        st.dataframe(df[['query_id', 'reason', 'priority', 'created_at']], use_container_width=True)
    else:
        st.info("No open escalation tickets")
    
    st.divider()
    
    # Escalation by category
    st.subheader("Escalations by Category")
    by_category = escalation_rules.get_escalation_by_category()
    if by_category:
        df = pd.DataFrame(by_category)
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df.set_index('category')[['escalation_count']])
        with col2:
            st.line_chart(df.set_index('category')[['escalation_rate']])


# ==================== KNOWLEDGE BASE ====================
elif page == "Knowledge Base":
    st.title("📚 Knowledge Base Management")
    
    learning_stats = knowledge_updater.get_learning_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Learned Responses", learning_stats['total_learned_responses'])
    with col2:
        st.metric("Total Reuses", learning_stats['total_reuses'])
    with col3:
        st.metric("Avg Reuses", f"{learning_stats['avg_reuses_per_response']:.1f}")
    with col4:
        st.metric("Categories", learning_stats['categories_with_learning'])
    
    st.divider()
    
    # Coverage by category
    st.subheader("Learning Coverage by Category")
    coverage = knowledge_updater.get_category_learning_coverage()
    if coverage:
        df = pd.DataFrame(coverage)
        st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Top learned responses
    st.subheader("Top Reused Learned Responses")
    top_learned = knowledge_updater.get_top_learned_responses(10)
    if top_learned:
        for i, item in enumerate(top_learned, 1):
            with st.expander(f"#{i} - {item['category']} ({item['times_reused']} reuses)"):
                st.write(item['tier2_response'][:200])


# ==================== USER MANAGEMENT ====================
elif page == "User Management":
    st.title("👥 User Management")
    
    col1, col2, col3 = st.columns(3)
    
    users = user_manager.get_all_users()
    active_users = user_manager.get_active_users(30)
    
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        st.metric("Active (30d)", len(active_users))
    with col3:
        st.metric("Support Staff", len([u for u in users if u['role'] != 'customer']))
    
    st.divider()
    
    # User list
    st.subheader("User Accounts")
    if users:
        df = pd.DataFrame(users)
        st.dataframe(df[['username', 'email', 'role', 'is_active', 'created_at']], use_container_width=True)
    
    st.divider()
    
    # User roles
    st.subheader("Users by Role")
    role_distribution = {}
    for user in users:
        role = user['role']
        role_distribution[role] = role_distribution.get(role, 0) + 1
    
    if role_distribution:
        df = pd.DataFrame(list(role_distribution.items()), columns=['Role', 'Count'])
        st.bar_chart(df.set_index('Role'))


# ==================== AUDIT LOGS ====================
elif page == "Audit Logs":
    st.title("📋 Audit Logs & Compliance")
    
    # Compliance report
    days = st.sidebar.slider("Report Period (days)", 1, 180, 90)
    compliance_report = audit_logger.compliance_report(days)
    
    st.subheader("Compliance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Actions", compliance_report['summary']['total_actions'])
    with col2:
        st.metric("Unique Users", compliance_report['summary']['unique_users'])
    with col3:
        st.metric("Resource Types", compliance_report['summary']['resource_types'])
    with col4:
        st.metric("High Risk Ops", compliance_report['high_risk_operations'])
    
    st.divider()
    
    # Actions by type
    st.subheader("Actions Distribution")
    actions = compliance_report['actions_by_type']
    if actions:
        df = pd.DataFrame(list(actions.items()), columns=['Action', 'Count'])
        st.bar_chart(df.set_index('Action'))
    
    st.divider()
    
    # Recent audit logs
    st.subheader("Recent Audit Activity")
    audit_logs = audit_logger.get_audit_trail(None, 20)
    if audit_logs:
        df = pd.DataFrame(audit_logs)
        st.dataframe(df[['user_id', 'action', 'resource_type', 'timestamp']], use_container_width=True)


# ==================== SYSTEM HEALTH ====================
elif page == "System Health":
    st.title("🏥 System Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cache Performance")
        cache_stats = db.execute_query("SELECT COUNT(*) as count FROM cache_entries WHERE expires_at > CURRENT_TIMESTAMP")[0]
        st.metric("Cached Queries", cache_stats['count'])
        
        try:
            from features.cache_manager import CacheManager
            cache_manager = CacheManager(db)
            efficiency = cache_manager.calculate_cache_efficiency()
            st.metric("Cache Efficiency", f"{efficiency['cache_efficiency_percentage']:.1f}%")
        except:
            st.info("Cache not available")
    
    with col2:
        st.subheader("Database Health")
        st.info("✓ Database connected")
        
        queries_count = db.execute_query("SELECT COUNT(*) as count FROM queries")[0]
        st.metric("Total Records", queries_count['count'])
    
    st.divider()
    
    st.success("✓ System is operating normally")
