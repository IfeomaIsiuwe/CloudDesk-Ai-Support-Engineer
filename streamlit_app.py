"""
CloudDesk AI Support Engineer - Main Application
Fully integrated with all features: metrics, feedback, learning, escalations, etc.
"""
import os
import time
import hashlib
import streamlit as st
from huggingface_hub import InferenceClient

from retrieval_pipeline import (
    load_config,
    get_vector_store,
    run_rag_pipeline,
)

from database import DatabaseManager
from features import (
    MetricsTracker,
    FeedbackSystem,
    KnowledgeUpdater,
    SessionManager,
    EscalationRules,
    CacheManager,
    TaggingSystem,
    NotificationHandler,
    SearchAnalytics
)


st.set_page_config(
    page_title="CloudDesk AI Support Engineer",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================== CUSTOM CSS ====================
def inject_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00d9ff;
    }
    
    .stApp { background-color: #ffffff; }
    
    .header-container {
        background: linear-gradient(135deg, #0066cc 0%, #00d9ff 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.15);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    .stChatMessage.user {
        background: linear-gradient(135deg, #f0f4ff 0%, #f5e6ff 100%);
        border-left: 4px solid #0066cc;
    }
    
    .stChatMessage.assistant {
        background: linear-gradient(135deg, #f0fff9 0%, #e6f9ff 100%);
        border-left: 4px solid #00d9ff;
    }
    
    .metric-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-card:hover {
        border-color: #0066cc;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.1);
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #0066cc;
        font-size: 1.8rem;
        font-weight: 800;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff9e6 0%, #fff5e6 100%);
        border-left: 4px solid #ff9900;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .danger-box {
        background: linear-gradient(135deg, #ffe6e6 0%, #fff0f0 100%);
        border-left: 4px solid #ff3333;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== INITIALIZATION ====================

# Load environment variables
try:
    for key in ["HF_TOKEN", "HF_MODEL", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass


@st.cache_resource
def initialise_pipeline():
    """Initialize RAG pipeline"""
    cfg = load_config()
    vstore = get_vector_store(cfg)
    client = InferenceClient(api_key=cfg["hf_token"]) if cfg.get("hf_token") else None
    return cfg, vstore, client


@st.cache_resource
def init_db():
    """Initialize database and create tables"""
    db = DatabaseManager()
    return db


def get_or_create_session(db: DatabaseManager):
    """Get or create session for current user"""
    if 'session_id' not in st.session_state:
        user_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        st.session_state.user_id = user_id
        
        session_manager = SessionManager(db)
        st.session_state.session_id = session_manager.create_session(user_id)
    
    return st.session_state.session_id, st.session_state.user_id


# ==================== MAIN APP ====================

inject_custom_css()

# Initialize
db = init_db()
session_id, user_id = get_or_create_session(db)

# Initialize feature managers
session_manager = SessionManager(db)
tagging_system = TaggingSystem(db)
escalation_rules = EscalationRules(db)
cache_manager = CacheManager(db)
feedback_system = FeedbackSystem(db)
knowledge_updater = KnowledgeUpdater(db)
search_analytics = SearchAnalytics(db)
metrics_tracker = MetricsTracker(db)

# Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🚀 CloudDesk AI Support Engineer</h1>
        <p class="header-subtitle">Intelligent assistance powered by retrieval-augmented generation</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #555;">
        <p style="font-size: 1rem; line-height: 1.6;">
        Ask any CloudDesk support question and receive an intelligent response 
        based on our comprehensive knowledge base.
        </p>
    </div>
    """, unsafe_allow_html=True)

try:
    cfg, vstore, client = initialise_pipeline()

    question = st.chat_input("💬 Ask a CloudDesk support question...", key="chat_input")

    if question:
        # Auto-categorize
        category, tags = tagging_system.auto_categorize(question)
        
        # Check cache
        cache_result = cache_manager.get_cached_result(question)
        
        if cache_result:
            st.info("📦 Using cached response")
            result = cache_result
            from_cache = True
        else:
            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)

            # Get response
            with st.chat_message("assistant", avatar="🤖"):
                start_time = time.perf_counter()

                with st.spinner("🔍 Searching knowledge base..."):
                    result = run_rag_pipeline(cfg, vstore, client, question)
                
                response_time = time.perf_counter() - start_time
                
                # Store in database
                query_id = session_manager.add_query_to_session(session_id, user_id, question)
                db.update_query_category(query_id, category, tags)
                
                confidence_pct = float(result.get('confidence_pct', '0%').rstrip('%')) / 100
                response_id = db.insert_response(
                    query_id,
                    result["answer"],
                    confidence_pct,
                    response_time * 1000,
                    result.get("citations", "").split('\n') if result.get("citations") else []
                )
                
                # Cache result
                cache_manager.cache_result(question, result)
                search_analytics.record_search(question, category)
                
                from_cache = False
        
        # Display response
        if from_cache:
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(result["answer"])
            
            # Metrics
            confidence_pct = float(result.get('confidence_pct', '0%').rstrip('%'))
            response_time_ms = result.get('response_time_ms', 0)
            if not isinstance(response_time_ms, (int, float)):
                response_time_ms = 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⏱️ Response Time</div>
                    <div class="metric-value">{response_time_ms/1000:.2f}s</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                confidence_level = "🟢" if confidence_pct >= 60 else "🟡"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{confidence_level} Confidence</div>
                    <div class="metric-value">{confidence_pct:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                should_escalate = escalation_rules.should_escalate(confidence_pct / 100, category)
                status = "⚠️ Escalated" if should_escalate else "✅ Standard"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Status</div>
                    <div class="metric-value" style="font-size: 1.2rem;">{status}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Escalation
            if should_escalate:
                if not from_cache:
                    escalation_ticket_id = escalation_rules.create_escalation(
                        query_id,
                        f"Confidence: {confidence_pct:.1f}%",
                        "medium"
                    )
                
                st.markdown("""
                <div class="warning-box">
                    <strong>⚠️ Escalation Notice</strong><br>
                    This has been escalated to Tier-2 Support for specialist review.
                </div>
                """, unsafe_allow_html=True)
            
            # Check learned responses
            if category:
                learned = knowledge_updater.get_similar_learned_response(category, confidence_pct / 100)
                if learned:
                    st.info("💡 This was learned from a previous support interaction!")
            
            # Sources
            if result.get("citations"):
                with st.expander("📚 View Sources & References", expanded=False):
                    st.markdown(result["citations"])
            else:
                st.info("💡 No sources available for this query.")
            
            st.divider()
            
            # Feedback
            st.subheader("📝 Your Feedback")
            col1, col2 = st.columns([1, 3])
            
            with col1:
                helpful = st.radio(
                    "Helpful?",
                    ["👍 Yes", "👎 No"],
                    key=f"helpful_{query_id if not from_cache else 'cached'}"
                )
                rating = st.select_slider(
                    "Rate:",
                    range(1, 6),
                    value=3,
                    key=f"rating_{query_id if not from_cache else 'cached'}"
                )
            
            with col2:
                comment = st.text_area(
                    "Comments:",
                    key=f"comment_{query_id if not from_cache else 'cached'}",
                    height=80
                )
            
            if st.button("Submit Feedback", key=f"submit_{query_id if not from_cache else 'cached'}"):
                if not from_cache:
                    feedback_system.submit_feedback(
                        query_id,
                        response_id,
                        user_id,
                        rating,
                        helpful == "👍 Yes",
                        comment if comment else None
                    )
                st.success("✅ Thank you for your feedback!")
    
    # Sidebar stats
    with st.sidebar:
        st.subheader("📊 Your Stats")
        user_stats = session_manager.get_user_analytics(user_id)
        st.metric("Sessions", user_stats['total_sessions'])
        st.metric("Queries", user_stats['total_queries'])
        st.metric("Escalations", user_stats['total_escalations'])

except Exception as e:
    st.markdown("""
    <div class="danger-box">
        <strong>❌ Error Starting Assistant</strong><br>
        The CloudDesk support assistant could not be initialized.
    </div>
    """, unsafe_allow_html=True)
    st.exception(e)
