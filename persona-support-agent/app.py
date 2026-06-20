import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import sys
import json
import uuid
import pandas as pd
import altair as alt
import streamlit as st

# Force virtual env libraries path injection if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.escalator import check_escalation_rules
from src.generator import generate_adaptive_response
from src import config

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Persona-Adaptive Customer Support Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Glassmorphism CSS Injector ---
def inject_custom_styles():
    st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #090B11 0%, #0F131E 60%, #15112B 100%) !important;
        color: #F8FAFC !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090B12 0%, #0F131E 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Glassmorphic Card Style */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
    }
    
    /* Shifting animated gradient title */
    .glow-header {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(120deg, #6366F1, #8B5CF6, #EC4899, #6366F1);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(99, 102, 241, 0.35);
        margin-bottom: 1.5rem;
        animation: gradient-shift 8s ease infinite;
        letter-spacing: -0.5px;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Premium Tab Customization */
    button[data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        color: #94A3B8 !important;
        transition: all 0.3s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        color: #F8FAFC !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(99, 102, 241, 0.15) !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
        color: #F8FAFC !important;
        box-shadow: 0 -4px 15px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Custom Metric Display */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.35) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(8px) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.3) !important;
        box-shadow: 0 4px 25px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Chat Bubbles */
    .chat-bubble-user {
        background: rgba(99, 102, 241, 0.18);
        border-right: 4px solid #6366F1;
        border-radius: 12px 12px 0 12px;
        padding: 12px 16px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        text-align: left;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .chat-bubble-agent {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #10B981;
        border-radius: 12px 12px 12px 0;
        padding: 12px 16px;
        margin: 10px auto 10px 0;
        max-width: 80%;
        text-align: left;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .chat-bubble-human {
        background: rgba(245, 158, 11, 0.15);
        border-left: 4px solid #F59E0B;
        border-radius: 12px 12px 12px 0;
        padding: 12px 16px;
        margin: 10px auto 10px 0;
        max-width: 80%;
        text-align: left;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .chat-label {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-bottom: 3px;
        font-weight: 500;
    }
    
    /* Persona Badges */
    .persona-badge {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 30px;
        display: inline-flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .badge-tech {
        background: rgba(59, 130, 246, 0.2);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.4);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
    }
    .badge-frustrated {
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.2);
    }
    .badge-exec {
        background: rgba(167, 139, 250, 0.2);
        color: #C084FC;
        border: 1px solid rgba(167, 139, 250, 0.4);
        box-shadow: 0 0 12px rgba(167, 139, 250, 0.2);
    }
    
    /* Pulsing Alert */
    .pulse-escalated {
        background: rgba(220, 38, 38, 0.15);
        border: 1px solid rgba(220, 38, 38, 0.4);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        animation: pulse-border 2s infinite;
    }
    @keyframes pulse-border {
        0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(220, 38, 38, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    
    /* Candidate Status Indicator */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    /* Code container styles */
    code {
        color: #F472B6 !important;
        background-color: rgba(30, 41, 59, 0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_styles()

# --- Initialize Session States ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "tickets" not in st.session_state:
    st.session_state.tickets = {}
if "current_ticket_id" not in st.session_state:
    st.session_state.current_ticket_id = str(uuid.uuid4())
if "metrics_log" not in st.session_state:
    st.session_state.metrics_log = []
if "force_refresh" not in st.session_state:
    st.session_state.force_refresh = False

# --- API Key and Environment Setup ---
# Check .env first.
env_key = os.environ.get("GEMINI_API_KEY", "")


if env_key:
    config.GEMINI_API_KEY = env_key
else:
    st.sidebar.markdown("<h3 style='margin-top:0;'>🔑 API Authentication</h3>", unsafe_allow_html=True)
    user_api_key = st.sidebar.text_input("Enter Google Gemini API Key:", type="password")
    if user_api_key:
        os.environ["GEMINI_API_KEY"] = user_api_key
        config.GEMINI_API_KEY = user_api_key
        st.sidebar.success("API Key activated!")
        st.rerun()

# Initialize RAG Pipeline
@st.cache_resource
def get_rag_pipeline():
    return LocalRAGPipeline()

rag = get_rag_pipeline()

# Get DB count
db_count = 0
try:
    db_count = rag.collection.count()
except Exception as e:
    pass

# Wrap Admin and Database Controls in a collapsed expander for a clean customer-facing UI
with st.sidebar.expander("🛠️ Admin & Database Controls", expanded=False):
    st.markdown("<h4 style='margin-top:0;'>🔑 API Status</h4>", unsafe_allow_html=True)
    if env_key:
        st.success("Loaded from environment")
    else:
        st.info("Configured manually")
        
    st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    
    st.markdown("<h4>📂 Database Manager</h4>", unsafe_allow_html=True)
    st.metric("Indexed Chunks Count", db_count)
    
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    if not os.path.exists(data_path) or db_count == 0:
        st.warning("Knowledge Base is empty.")
        if st.button("Generate & Index KB"):
            with st.spinner("Generating KB files and indexing..."):
                from scripts.generate_kb import create_kb_documents
                create_kb_documents(data_path)
                rag.ingest_directory(data_path, force_reindex=True)
            st.success("Database populated!")
            st.rerun()
    else:
        if st.button("Force Database Re-index"):
            with st.spinner("Re-indexing KB files..."):
                rag.ingest_directory(data_path, force_reindex=True)
            st.success("Database re-indexed!")
            st.rerun()


# --- Main App Layout ---
st.markdown("<div class='glow-header'>🤖 Persona-Adaptive Support Hub</div>", unsafe_allow_html=True)

# Tabs
tab_chat, tab_live_desk, tab_analytics, tab_kb = st.tabs([
    "💬 Support Chatbot", 
    "👨‍💻 Human Agent Desk", 
    "📊 Analytics Hub", 
    "📚 Knowledge Base Docs"
])

# =========================================================================
# TAB 1: Support Chatbot
# =========================================================================
with tab_chat:
    col_chat, col_inspect = st.columns([5, 3])
    
    with col_chat:
        st.subheader("Customer Interaction Portal")
        
        # Display custom chat history
        chat_container = st.container(height=480)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("<p style='text-align: center; color: #64748B; margin-top: 50px;'>Hello! Please describe your support inquiry below. Our persona-adaptive system will respond shortly.</p>", unsafe_allow_html=True)
            
            for msg in st.session_state.chat_history:
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    st.markdown(f"<div class='chat-label' style='text-align: right;'>Customer</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='chat-bubble-user'>{content}</div>", unsafe_allow_html=True)
                elif role == "assistant":
                    st.markdown(f"<div class='chat-label'>AI Support Agent ({msg.get('persona', 'Standard')})</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='chat-bubble-agent'>{content}</div>", unsafe_allow_html=True)
                elif role == "human":
                    st.markdown(f"<div class='chat-label' style='color:#F59E0B;'>Human Support Specialist</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='chat-bubble-human'>{content}</div>", unsafe_allow_html=True)
        
        # User input box
        if not config.GEMINI_API_KEY:
            st.warning("Please configure your Google Gemini API Key in the sidebar to send messages.")
        else:
            # Check if current ticket is already escalated
            current_ticket = st.session_state.tickets.get(st.session_state.current_ticket_id, {})
            is_escalated = current_ticket.get("status") == "Escalated"
            
            if is_escalated:
                st.info("🔒 This ticket has been transferred to a Live Human Agent. AI responses are paused. The agent will reply soon in the Human Agent Desk tab.")
                
                # Option to start a new chat
                if st.button("Start New Conversation"):
                    st.session_state.current_ticket_id = str(uuid.uuid4())
                    st.session_state.chat_history = []
                    st.rerun()
            else:
                user_msg = st.chat_input("Type your message here...")
                
                if user_msg:
                    # Append user message
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    
                    with st.spinner("Analyzing and retrieving context..."):
                        # 1. Classify Persona
                        persona_data = classify_customer_persona(user_msg)
                        persona = persona_data["persona"]
                        
                        # 2. Retrieve Documents
                        context = rag.retrieve_context(user_msg, top_k=3)
                        
                        # 3. Check Escalation
                        should_escalate, reason, handoff_data = check_escalation_rules(
                            user_msg, persona_data, context, st.session_state.chat_history[:-1]
                        )
                        
                        # Calculate best similarity score for metrics log
                        best_score = max([c["score"] for c in context]) if context else 0.0
                        
                        # Record metrics in log
                        st.session_state.metrics_log.append({
                            "timestamp": pd.Timestamp.now(),
                            "query": user_msg,
                            "persona": persona,
                            "sentiment": persona_data["sentiment"],
                            "best_score": best_score,
                            "escalated": should_escalate,
                            "reason": reason if should_escalate else "N/A"
                        })
                        
                        # Update st.session_state.tickets
                        st.session_state.tickets[st.session_state.current_ticket_id] = {
                            "id": st.session_state.current_ticket_id,
                            "user_query": user_msg,
                            "chat_history": list(st.session_state.chat_history),
                            "persona": persona,
                            "sentiment": persona_data["sentiment"],
                            "similarity_score": best_score,
                            "status": "Escalated" if should_escalate else "Active",
                            "handoff_data": handoff_data,
                            "retrieved_context": context
                        }
                        
                        # 4. Generate response or handle escalation
                        if should_escalate:
                            response_text = "I apologize, but I am unable to locate the precise solution to your request. I am connecting you with a live human support specialist."
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response_text,
                                "persona": "Escalated",
                                "metadata": persona_data
                            })
                            # Update ticket chat history
                            st.session_state.tickets[st.session_state.current_ticket_id]["chat_history"] = list(st.session_state.chat_history)
                        else:
                            response_text = generate_adaptive_response(user_msg, persona, context)
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response_text,
                                "persona": persona,
                                "metadata": persona_data
                            })
                            # Update ticket chat history
                            st.session_state.tickets[st.session_state.current_ticket_id]["chat_history"] = list(st.session_state.chat_history)
                            
                    st.rerun()
                    
    with col_inspect:
        st.subheader("System State Insights")
        
        current_ticket = st.session_state.tickets.get(st.session_state.current_ticket_id, {})
        
        if not current_ticket:
            st.markdown("<div class='glass-card'><p style='color:#94A3B8; text-align:center; margin:0;'>Send a message to see RAG retrieval diagnostics and persona classification rules.</p></div>", unsafe_allow_html=True)
        else:
            # 1. Display Persona Badge
            persona = current_ticket.get("persona")
            sentiment = current_ticket.get("sentiment")
            
            badge_class = "badge-tech" if persona == "Technical Expert" else "badge-frustrated" if persona == "Frustrated User" else "badge-exec"
            
            st.markdown(f"""
            <div class='glass-card'>
                <h4 style='margin-top:0; margin-bottom:10px; color:#F1F5F9;'>Classification Metrics</h4>
                <div class="persona-badge {badge_class}">👤 {persona}</div>
                <div style='margin-top:5px; font-size:0.95rem;'><b>Customer Sentiment:</b> {sentiment}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Display Escalation Alert if escalated
            if current_ticket.get("status") == "Escalated":
                handoff = current_ticket.get("handoff_data", {})
                st.markdown(f"""
                <div class="pulse-escalated">
                    <h4 style="color:#EF4444; margin-top:0; margin-bottom:5px;">⚠️ Escalated to Human Queue</h4>
                    <p style="font-size:0.9rem; margin-bottom:10px;"><b>Reason:</b> {handoff.get('escalation_reason', 'Low confidence')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🔍 View JSON Handoff Summary"):
                    st.code(json.dumps(handoff, indent=2), language="json")
            
            # 3. RAG Retrieval Inspector
            context_list = current_ticket.get("retrieved_context", [])
            st.markdown("<h4 style='margin-bottom:10px; color:#F1F5F9;'>RAG Retrieval Inspector</h4>", unsafe_allow_html=True)
            
            if not context_list:
                st.info("No documents searched or retrieved.")
            else:
                for idx, chunk in enumerate(context_list):
                    score_color = "#34D399" if chunk["score"] >= 0.5 else "#F59E0B" if chunk["score"] >= 0.4 else "#EF4444"
                    st.markdown(f"""
                    <div class='glass-card' style='padding: 12px; font-size: 0.9rem;'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                            <b style='color:#60A5FA;'>📄 {chunk['source']} (Page {chunk['page']})</b>
                            <b style='color:{score_color};'>Cosine Sim: {chunk['score']}</b>
                        </div>
                        <p style='color:#CBD5E1; margin:0; line-height: 1.3;'>"{chunk['text'][:180]}..."</p>
                    </div>
                    """, unsafe_allow_html=True)

# =========================================================================
# TAB 2: Live Agent Desk (Human-in-the-Loop Workflow)
# =========================================================================
with tab_live_desk:
    st.subheader("Human Support Specialist Workspace")
    st.markdown("<p style='color:#94A3B8; margin-top:-10px; margin-bottom:20px;'>Simulate the live human workspace. View escalated customer conversations, inspect tickets, and submit manual responses to complete the ticket loop.</p>", unsafe_allow_html=True)
    
    # Filter escalated tickets
    escalated_tickets = {tid: t for tid, t in st.session_state.tickets.items() if t.get("status") == "Escalated"}
    
    if not escalated_tickets:
        st.success("🎉 Excellent! The escalated ticket queue is currently empty. No active customer needs human intervention.")
    else:
        col_list, col_workspace = st.columns([1, 2])
        
        with col_list:
            st.markdown("<b>Active Escalated Queue</b>", unsafe_allow_html=True)
            selected_tid = st.radio(
                "Select a pending ticket:",
                options=list(escalated_tickets.keys()),
                format_func=lambda x: f"Ticket #{x[:6]} - {escalated_tickets[x]['persona']} ({escalated_tickets[x]['sentiment']})"
            )
            
        with col_workspace:
            if selected_tid:
                t = escalated_tickets[selected_tid]
                handoff = t.get("handoff_data", {})
                
                st.markdown(f"""
                <div class='glass-card' style='border-color: rgba(245, 158, 11, 0.4);'>
                    <h3 style='margin-top:0; color:#F59E0B;'>Ticket Workspace (ID: #{selected_tid[:8]})</h3>
                    <p><b>Customer Inquiry:</b> "{t['user_query']}"</p>
                    <p><b>Detected Persona:</b> <span class="persona-badge badge-tech" style="padding: 2px 8px; font-size:0.8rem;">{t['persona']}</span></p>
                    <p><b>Handoff Recommendation:</b> <code style="padding:4px; font-size:0.85rem;">{handoff.get('recommended_action', 'Review ticket')}</code></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable JSON report
                with st.expander("📋 View Core Handoff JSON Report"):
                    st.json(handoff)
                
                # Chat transcript history
                st.markdown("<b>Ticket Conversation Transcript</b>", unsafe_allow_html=True)
                history_container = st.container(height=240)
                with history_container:
                    for h_msg in t.get("chat_history", []):
                        role_name = "Customer" if h_msg["role"] == "user" else "AI Agent" if h_msg["role"] == "assistant" else "Human Agent"
                        bubble_style = "chat-bubble-user" if h_msg["role"] == "user" else "chat-bubble-agent" if h_msg["role"] == "assistant" else "chat-bubble-human"
                        st.markdown(f"<div class='chat-label'>{role_name}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='{bubble_style}'>{h_msg['content']}</div>", unsafe_allow_html=True)
                
                # Live human reply editor
                human_reply = st.text_area("Type your Human Response to send to the Customer:", placeholder="Hi, I am the lead billing engineer. I inspected our Stripe payment logs and discovered...")
                
                col_btn_resolve, col_btn_cancel = st.columns([1, 1])
                with col_btn_resolve:
                    if st.button("🚀 Send Response & Resolve Ticket", type="primary"):
                        if not human_reply.strip():
                            st.error("Please enter a response message before resolving the ticket.")
                        else:
                            # Update actual chat history in st.session_state
                            # Find matching history in session state
                            st.session_state.chat_history.append({"role": "human", "content": human_reply})
                            
                            # Update ticket status to Resolved
                            st.session_state.tickets[selected_tid]["chat_history"] = list(st.session_state.chat_history)
                            st.session_state.tickets[selected_tid]["status"] = "Resolved"
                            
                            # Mark in metrics
                            for m in st.session_state.metrics_log:
                                if m["query"] == t["user_query"]:
                                    m["escalated"] = False # update status in analytics logs
                            
                            st.success(f"Ticket #{selected_tid[:6]} resolved and response delivered successfully!")
                            st.rerun()

# =========================================================================
# TAB 3: Analytics Hub
# =========================================================================
with tab_analytics:
    st.subheader("Support Operational Analytics")
    
    if not st.session_state.metrics_log:
        st.info("No analytics data available. Engage in support conversations to populate the analytics dashboards.")
    else:
        # Load logs into DataFrame
        df = pd.DataFrame(st.session_state.metrics_log)
        
        # Calculate stats
        total_queries = len(df)
        escalated_count = sum(df["escalated"])
        escalation_rate = (escalated_count / total_queries) if total_queries > 0 else 0.0
        avg_confidence = df["best_score"].mean()
        
        # Render Key metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Inquiries", total_queries)
        col_m2.metric("Escalated Tickets", escalated_count)
        col_m3.metric("Escalation Rate", f"{escalation_rate:.1%}")
        col_m4.metric("Average Cosine Similarity", f"{avg_confidence:.3f}")
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin: 25px 0;'>", unsafe_allow_html=True)
        
        # Visual Charts
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("<b>Persona Frequency Distribution</b>", unsafe_allow_html=True)
            persona_df = df["persona"].value_counts().reset_index()
            persona_df.columns = ["Persona", "Count"]
            
            chart_persona = alt.Chart(persona_df).mark_bar().encode(
                x=alt.X('Persona:N', sort='-y'),
                y='Count:Q',
                color=alt.Color('Persona:N', scale=alt.Scale(range=['#3B82F6', '#EF4444', '#8B5CF6']))
            ).properties(height=240)
            st.altair_chart(chart_persona, use_container_width=True)
            
        with col_c2:
            st.markdown("<b>Customer Sentiment Profile</b>", unsafe_allow_html=True)
            sentiment_df = df["sentiment"].value_counts().reset_index()
            sentiment_df.columns = ["Sentiment", "Count"]
            
            chart_sentiment = alt.Chart(sentiment_df).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Sentiment", type="nominal", scale=alt.Scale(range=['#EF4444', '#6B7280', '#10B981']))
            ).properties(height=240)
            st.altair_chart(chart_sentiment, use_container_width=True)
            
        # Metrics Table
        st.markdown("<b>Support Log History</b>", unsafe_allow_html=True)
        st.dataframe(
            df[["timestamp", "query", "persona", "sentiment", "best_score", "escalated", "reason"]],
            use_container_width=True
        )

# =========================================================================
# TAB 4: Knowledge Base Docs
# =========================================================================
with tab_kb:
    st.subheader("Ingested Support Database Docs")
    st.markdown("<p style='color:#94A3B8; margin-top:-10px; margin-bottom:20px;'>Inspect raw documents in the /data knowledge base folder to verify RAG sourcing guidelines.</p>", unsafe_allow_html=True)
    
    if not os.path.exists(data_path):
        st.warning("Knowledge Base directory not found. Please click 'Generate & Index KB' in the sidebar.")
    else:
        files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
        
        if not files:
            st.info("No documents found in /data directory.")
        else:
            col_doc_list, col_doc_view = st.columns([1, 2])
            
            with col_doc_list:
                st.markdown("<b>Document List</b>", unsafe_allow_html=True)
                selected_file = st.radio(
                    "Select a file to inspect:",
                    options=files
                )
                
            with col_doc_view:
                if selected_file:
                    filepath = os.path.join(data_path, selected_file)
                    st.markdown(f"**Viewing: `{selected_file}`**")
                    
                    if selected_file.endswith('.pdf'):
                        # Read PDF using pypdf for review
                        try:
                            reader = PdfReader(filepath)
                            pdf_pages = [page.extract_text() for page in reader.pages]
                            page_select = st.selectbox("Select Page:", range(1, len(pdf_pages) + 1))
                            
                            st.markdown(f"""
                            <div class='glass-card' style='background: rgba(15,23,42,0.8); font-family:Courier; font-size:0.9rem;'>
                                {pdf_pages[page_select-1].replace(chr(10), '<br/>')}
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error rendering PDF: {e}")
                    else:
                        # Read raw txt/md
                        with open(filepath, "r", encoding="utf-8") as f:
                            doc_content = f.read()
                        
                        st.markdown(f"""
                        <div class='glass-card' style='background: rgba(15,23,42,0.8); font-family:Courier; font-size:0.9rem; white-space: pre-wrap;'>
                            {doc_content}
                        </div>
                        """, unsafe_allow_html=True)
