"""
Analytics Dashboard for CloudDesk
Run with: streamlit run dashboards/analytics_dashboard.py
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
    page_title="CloudDesk Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
db = DatabaseManager()
metrics_tracker = MetricsTracker(db)
feedback_system = FeedbackSystem(db)
knowledge_updater = KnowledgeUpdater(db)
search_analytics_mgr = SearchAnalytics(db)
tagging_system = TaggingSystem(db)


# Sidebar
st.sidebar.title("📊 Analytics Dashboard")
page = st.sidebar.radio("Select Analytics", [
    "Query Performance",
    "Search Analytics",
    "Feedback Analysis",
    "Knowledge Base Insights",
    "Category Analysis",
    "Trend Analysis"
])

# ==================== QUERY PERFORMANCE ====================
if page == "Query Performance":
    st.title("🎯 Query Performance Analytics")
    
    days = st.sidebar.slider("Select period (days)", 1, 90, 30)
    
    metrics = metrics_tracker.get_summary(days)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Success Rate", f"{metrics['resolved_percentage']:.1f}%", 
                 "% of queries resolved")
    with col2:
        st.metric("Escalation Rate", f"{metrics['escalated_percentage']:.1f}%",
                 "% requiring escalation")
    with col3:
        st.metric("Confidence Score", f"{metrics['avg_confidence']:.1%}",
                 "Average model confidence")
    with col4:
        st.metric("Response Time", f"{metrics['avg_response_time_ms']:.0f}ms",
                 "Average query response")
    
    st.divider()
    
    # Performance comparison
    st.subheader("Performance Metrics Over Time")
    col1, col2 = st.columns(2)
    
    with col1:
        # Resolution trend
        sql = """
            SELECT DATE(created_at) as date, 
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved
            FROM queries
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        data = db.execute_query(sql, (days,))
        if data:
            df = pd.DataFrame(data)
            st.line_chart(df.set_index('date')[['resolved']], use_container_width=True)
    
    with col2:
        # Confidence trend
        sql = """
            SELECT DATE(q.created_at) as date,
                   AVG(qr.confidence) as avg_confidence
            FROM queries q
            LEFT JOIN query_responses qr ON q.id = qr.query_id
            WHERE q.created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(q.created_at)
            ORDER BY date
        """
        data = db.execute_query(sql, (days,))
        if data:
            df = pd.DataFrame(data)
            st.line_chart(df.set_index('date')[['avg_confidence']], use_container_width=True)


# ==================== SEARCH ANALYTICS ====================
elif page == "Search Analytics":
    st.title("🔍 Search Analytics")
    
    search_summary = search_analytics_mgr.get_search_analytics_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Unique Queries", search_summary['total_unique_queries'])
    with col2:
        st.metric("Total Searches", search_summary['total_searches'])
    with col3:
        st.metric("Avg Success Rate", f"{search_summary['avg_success_rate']:.1%}")
    with col4:
        st.metric("Avg Response Time", f"{search_summary['avg_response_time_ms']:.0f}ms")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Queries")
        top_queries = search_analytics_mgr.get_top_queries(15)
        if top_queries:
            df = pd.DataFrame(top_queries)
            st.dataframe(df[['query', 'search_count', 'success_rate']], use_container_width=True)
    
    with col2:
        st.subheader("Search Trends")
        trends = search_analytics_mgr.get_search_trends(30)
        if trends['daily_trends']:
            df = pd.DataFrame(trends['daily_trends'])
            st.line_chart(df.set_index('date')[['search_count']], use_container_width=True)
    
    st.divider()
    
    # Knowledge gaps
    st.subheader("Knowledge Gaps - High Escalation Queries")
    gaps = search_analytics_mgr.get_knowledge_gap_analysis()
    if gaps:
        df = pd.DataFrame(gaps)
        st.warning("These queries escalate frequently and should have better KB coverage")
        st.dataframe(df, use_container_width=True)


# ==================== FEEDBACK ANALYSIS ====================
elif page == "Feedback Analysis":
    st.title("⭐ Feedback & Rating Analysis")
    
    days = st.sidebar.slider("Select period (days)", 1, 90, 30)
    
    feedback_summary = feedback_system.get_feedback_summary(days)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Feedback", feedback_summary['total_feedback'])
    with col2:
        st.metric("Helpful %", f"{feedback_summary['helpful_percentage']:.1f}%")
    with col3:
        st.metric("Avg Rating", f"{feedback_summary['average_rating']:.2f} ⭐")
    with col4:
        st.metric("Needs Improvement", feedback_summary['needs_improvement_count'])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rating Distribution")
        rating_dist = feedback_system.get_rating_distribution(days)
        if rating_dist:
            df = pd.DataFrame(list(rating_dist.items()), columns=['Rating', 'Count'])
            st.bar_chart(df.set_index('Rating'))
    
    with col2:
        st.subheader("Helpful vs Unhelpful")
        helpful_data = {
            "Helpful": feedback_summary['helpful_percentage'],
            "Not Helpful": 100 - feedback_summary['helpful_percentage']
        }
        df = pd.DataFrame(list(helpful_data.items()), columns=['Type', 'Percentage'])
        st.bar_chart(df.set_index('Type'))
    
    st.divider()
    
    # Feedback by category
    st.subheader("Ratings by Category")
    by_category = feedback_system.get_feedback_by_category(days)
    if by_category:
        df = pd.DataFrame(by_category)
        st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Low rated queries
    st.subheader("Low Rated Responses (Need Improvement)")
    low_rated = feedback_system.get_low_rated_queries(2, 10)
    if low_rated:
        for item in low_rated:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"❌ {item['question'][:80]}")
                st.caption(f"Rating: {item['rating']}/5 - {item['comment']}")
            with col2:
                st.write(f"⭐ {item['rating']}/5")


# ==================== KNOWLEDGE BASE INSIGHTS ====================
elif page == "Knowledge Base Insights":
    st.title("📚 Knowledge Base Insights")
    
    learning_stats = knowledge_updater.get_learning_statistics()
    effectiveness = knowledge_updater.calculate_learning_effectiveness()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Learned Responses", learning_stats['total_learned_responses'])
    with col2:
        st.metric("Total Reuses", learning_stats['total_reuses'])
    with col3:
        st.metric("Avg Reuses", f"{learning_stats['avg_reuses_per_response']:.1f}")
    with col4:
        st.metric("Effectiveness", f"{effectiveness['effectiveness_score']:.1f}%")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Learned Responses")
        top_learned = knowledge_updater.get_top_learned_responses(10)
        if top_learned:
            df = pd.DataFrame(top_learned)
            st.dataframe(df[['category', 'times_reused', 'confidence_threshold']], use_container_width=True)
    
    with col2:
        st.subheader("Learning Opportunities")
        suggestions = knowledge_updater.suggest_new_learning_areas(30, 3)
        if suggestions:
            df = pd.DataFrame(suggestions)
            st.warning("These categories need more learned responses")
            st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Coverage analysis
    st.subheader("Coverage by Category")
    coverage = knowledge_updater.get_category_learning_coverage()
    if coverage:
        df = pd.DataFrame(coverage)
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df.set_index('category')[['learned_responses']])
        with col2:
            st.line_chart(df.set_index('category')[['total_reuses']])


# ==================== CATEGORY ANALYSIS ====================
elif page == "Category Analysis":
    st.title("📂 Category Performance Analysis")
    
    # Category distribution
    st.subheader("Query Distribution by Category")
    category_dist = tagging_system.get_category_distribution()
    
    if category_dist:
        df = pd.DataFrame(list(category_dist.items()), columns=['Category', 'Count'])
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(df.set_index('Category'))
        with col2:
            st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Category health
    st.subheader("Category Health Metrics")
    category_health = tagging_system.get_category_health()
    
    if category_health:
        for category, health in category_health.items():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(f"{category} - Total", health['total_queries'])
            with col2:
                st.metric(f"{category} - Success %", f"{health['success_rate']:.1f}%")
            with col3:
                st.metric(f"{category} - Escalation %", f"{health['escalation_rate']:.1f}%")
            with col4:
                st.metric(f"{category} - Avg Confidence", f"{health['avg_confidence']:.1%}")
            st.divider()


# ==================== TREND ANALYSIS ====================
elif page == "Trend Analysis":
    st.title("📈 Trend Analysis")
    
    days = st.sidebar.slider("Select period (days)", 7, 90, 30)
    
    # Escalation trends
    st.subheader("Escalation Trend")
    trends = metrics_tracker.get_trend_data(days)
    
    if trends['escalation_trends']:
        df = pd.DataFrame(trends['escalation_trends'])
        col1, col2 = st.columns(2)
        
        with col1:
            st.line_chart(df.set_index('date')[['total']], use_container_width=True)
            st.caption("Total queries per day")
        
        with col2:
            st.line_chart(df.set_index('date')[['escalated']], use_container_width=True)
            st.caption("Escalations per day")
    
    st.divider()
    
    # Trending categories
    st.subheader("Trending Query Categories")
    if trends['trending_categories']:
        df = pd.DataFrame(trends['trending_categories'])
        st.bar_chart(df.set_index('category')[['count']])
    
    st.divider()
    
    # Top queries trend
    st.subheader("Top Queries Trend")
    top_queries = search_analytics_mgr.get_top_queries(10)
    if top_queries:
        df = pd.DataFrame(top_queries)
        st.dataframe(df[['query', 'search_count', 'last_searched']], use_container_width=True)
