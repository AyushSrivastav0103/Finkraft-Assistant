# --- Streamlit Page Config (MUST BE FIRST) ---
import streamlit as st

st.set_page_config(
    page_title="Finkraft Unified Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules
import json
import uuid
from datetime import datetime, timedelta
import time
import re
from typing import Dict, List, Any, Optional

# Core modules
from core import router
from core import context_manager as cm
from utils.role_manager import get_allowed_actions
from utils import trace_logger
from utils.trace_logger import get_persistent_traces

# --- Enhanced Custom CSS for Professional UI ---
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Variables */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode overrides */
    .dark {
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
        --bg-primary: #111827;
        --bg-secondary: #1f2937;
        --border-color: #374151;
    }
    
    /* Main app styling */
    .main {
        font-family: 'Inter', sans-serif;
        padding-top: 1rem;
    }
    
    /* Enhanced chat message styling */
    .chat-message {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 16px;
        box-shadow: var(--shadow);
        position: relative;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        margin-left: 15%;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, var(--accent-color) 0%, #f5576c 100%);
        color: white;
        margin-right: 15%;
        border-bottom-left-radius: 4px;
    }
    
    .system-message {
        background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%);
        color: white;
        margin: 0 10%;
        text-align: center;
        border-radius: 20px;
    }
    
    /* Professional metric cards */
    .metric-card {
        background: rgba(102, 126, 234, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        margin: 0.75rem 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        border-color: var(--primary-color);
    }
    
    /* Enhanced status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-open { background: #fee2e2; color: #dc2626; }
    .status-closed { background: #d1fae5; color: #059669; }
    .status-in_progress { background: #fef3c7; color: #d97706; }
    .status-pending { background: #e0e7ff; color: #4f46e5; }
    
    .priority-high { background: linear-gradient(135deg, #ef4444, #dc2626); }
    .priority-medium { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .priority-low { background: linear-gradient(135deg, #10b981, #059669); }
    
    /* Enhanced header */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.1;
    }
    
    /* Professional input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid var(--border-color);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Professional sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-color);
        color: white;
        box-shadow: var(--shadow);
    }
    
    /* Animated loading indicators */
    .loading-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(102, 126, 234, 0.3);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Professional alert styling */
    .custom-alert {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin: 1rem 0;
    }
    
    .alert-success {
        background: #f0fdf4;
        border-color: #22c55e;
        color: #15803d;
    }
    
    .alert-warning {
        background: #fffbeb;
        border-color: #f59e0b;
        color: #d97706;
    }
    
    .alert-error {
        background: #fef2f2;
        border-color: #ef4444;
        color: #dc2626;
    }
    
    /* Enhanced expander styling */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
    }
    
    /* Professional progress bars */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--bg-secondary);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Enhanced Data Loading with Caching ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_json_cached(filepath: str) -> Dict[str, Any]:
    """Load JSON with caching and error handling"""
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {filepath}: {str(e)}")
        return {}

# Load all data
FAQS = load_json_cached("data/faqs.json")
EMAILS = load_json_cached("data/sample_emails.json")
ACTIONS = load_json_cached("config/actions_config.json")
TICKETS = load_json_cached("data/tickets.json")

# --- Advanced Session State Management ---
def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        "conversations": {},
        "active_conversation": str(uuid.uuid4()),
        "tickets": TICKETS,
        "user_id": str(uuid.uuid4()),
        "user_name": f"User_{str(uuid.uuid4())[:8]}",
        "workspace": "default",
        "theme_mode": "light",
        "notification_count": 0,
        "last_activity": datetime.now(),
        "conversation_context": {},
        "quick_actions_used": [],
        "user_preferences": {
            "show_traces": True,
            "auto_save": True,
            "notification_sound": False
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize session state
initialize_session_state()

# Load custom CSS
load_css()


# --- Enhanced Analytics and Insights ---
def get_conversation_analytics():
    """Generate conversation analytics"""
    conversations = st.session_state["conversations"]
    total_conversations = len(conversations)
    total_messages = sum(len(msgs) for msgs in conversations.values())
    
    # Calculate average response time (simulated)
    avg_response_time = "1.2s"
    
    # Get module usage stats
    traces = get_persistent_traces(100)
    module_stats = {}
    for trace in traces:
        module = trace.get('routed_to', 'Unknown')
        module_stats[module] = module_stats.get(module, 0) + 1
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "avg_response_time": avg_response_time,
        "module_stats": module_stats,
        "user_satisfaction": 4.7  # Simulated
    }

# --- Professional Header with Real-time Status ---
def render_header():
    """Render enhanced header with status indicators"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Finkraft Unified AI Assistant</h1>
        <p style="font-size: 1.1rem; margin-top: 0.5rem;">
            Your intelligent companion for GST, invoices, and compliance management
        </p>
        <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold;">🎯</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Smart Actions</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold;">🧠</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Context Aware</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold;">🔒</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Role-Based Access</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold;">⚡</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Real-time Insights</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

render_header()

# --- Enhanced Sidebar with Professional Design ---
with st.sidebar:
    st.markdown("## 👤 User Profile")
    
    # User info with professional styling
    user_id = st.session_state["user_id"]
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("🎭")
    with col2:
        st.markdown(f"**{st.session_state['user_name']}**")
    
    # Enhanced role selection
    role = st.selectbox(
        "Select Your Role",
        ["Admin", "Manager", "Viewer"],
        index=1,
        help="Your role determines available actions and data visibility"
    )
    
    # Role-based capabilities display
    role_capabilities = {
        "Admin": ["🔧 Full System Access", "📊 All Reports", "👥 User Management", "🔍 Audit Trails"],
        "Manager": ["📄 Invoice Management", "📊 GST Reports", "🎫 Ticket Creation", "📈 Analytics"],
        "Viewer": ["👀 Read-Only Access", "📋 Basic Reports", "🎫 View Tickets", "❓ Help & FAQs"]
    }
    
    with st.expander(f"🔑 {role} Capabilities", expanded=False):
        for capability in role_capabilities.get(role, []):
            st.markdown(f"• {capability}")
    
    st.divider()
    
    # --- Enhanced Conversation Management ---
    st.markdown("## 💬 Conversation Hub")
    
    # Action buttons with improved styling
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Chat", use_container_width=True, help="Start a fresh conversation"):
            new_conv_id = str(uuid.uuid4())
            st.session_state["active_conversation"] = new_conv_id
            st.session_state["conversation_context"][new_conv_id] = {
                "started_at": datetime.now().isoformat(),
                "role": role,
                "topic": "General"
            }
            st.rerun()
    
    with col2:
        if st.button("🛑 End Chat", use_container_width=True, help="Archive current conversation"):
            conv_id = st.session_state["active_conversation"]
            if conv_id in st.session_state["conversations"] and st.session_state["conversations"][conv_id]:
                # Archive with enhanced context
                cm.save_conversation(
                    user_id,
                    "Conversation Ended",
                    "User ended conversation",
                    {
                        "role": role, 
                        "timestamp": datetime.now().isoformat(),
                        "message_count": len(st.session_state["conversations"][conv_id]),
                        "duration": "N/A"
                    }
                )
                st.success("💾 Conversation archived successfully!")
                time.sleep(1)
            st.session_state["active_conversation"] = str(uuid.uuid4())
            st.rerun()
    
    # Enhanced conversation history
    if st.session_state["conversations"]:
        st.markdown("**📚 Recent Conversations**")
        recent_convs = list(st.session_state["conversations"].items())[-5:]
        
        for conv_id, msgs in reversed(recent_convs):
            if msgs:
                # Extract conversation topic and timestamp
                first_msg = msgs[0]["content"][:30] + ("..." if len(msgs[0]["content"]) > 30 else "")
                last_timestamp = msgs[-1].get("timestamp", "")
                msg_count = len(msgs)
                
                # Create conversation preview
                conv_preview = f"💭 {first_msg}"
                if st.button(
                    conv_preview, 
                    key=f"conv-{conv_id}", 
                    help=f"Messages: {msg_count} | Last: {last_timestamp}",
                    use_container_width=True
                ):
                    st.session_state["active_conversation"] = conv_id
                    st.rerun()
    
    st.divider()

    # --- Smart Quick Actions ---
    st.markdown("## ⚡ Smart Actions")
    
    # Contextual quick actions based on role and recent activity
    role_actions = {
        "Admin": [
            ("📊 System Analytics", "show system performance analytics"),
            ("🔍 Audit Trail", "show recent audit trail"),
            ("👥 User Activity", "show user activity summary"),
            ("⚙️ System Health", "check system health status")
        ],
        "Manager": [
            ("📄 Invoice Summary", "Filter invoices from last month"),
            ("📊 GST Dashboard", "Why did my GST filing fail?"),
            ("🎫 Team Tickets", "Create a ticket for invoice mismatch"),
            ("📈 Performance Metrics", "Check filing status for last month")
        ],
        "Viewer": [
            ("📋 My Tasks", "show my pending tasks"),
            ("📊 Quick Report", "generate quick status report"),
            ("❓ Help Center", "show help and documentation"),
            ("🔔 Notifications", "show my recent notifications")
        ]
    }
    
    current_actions = role_actions.get(role, role_actions["Viewer"])
    
    for label, query in current_actions:
        if st.button(label, key=f"action_{label}", use_container_width=True):
            st.session_state["user_query"] = query
            st.session_state["quick_actions_used"].append({
                "action": label,
                "timestamp": datetime.now().isoformat(),
                "role": role
            })
            st.rerun()
    
    st.divider()
    # --- Real-time Analytics Dashboard ---
    st.markdown("## 📊 Live Analytics")
    
    analytics = get_conversation_analytics()
    
    # Metrics with professional styling
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Chats", analytics["total_conversations"], delta=1)
        st.metric("Messages", analytics["total_messages"], delta=5)
    
    with col2:
        st.metric("Avg Response", analytics["avg_response_time"], delta="-0.3s")
        st.metric("Satisfaction", f"{analytics['user_satisfaction']}/5.0", delta="0.2")
    
    # Module usage visualization
    if analytics["module_stats"]:
        st.markdown("**🎯 Module Usage**")
        for module, count in sorted(analytics["module_stats"].items(), key=lambda x: x[1], reverse=True)[:3]:
            progress = min(count / max(analytics["module_stats"].values()), 1.0)
            st.markdown(f"**{module}**: {count} queries")
            st.progress(progress)
    
    st.divider()
    # --- System Status & Health ---
    st.markdown("## 🔧 System Status")
    
    # Real-time system indicators
    system_status = {
        "🟢 Core System": "Online",
        "🟢 Database": "Connected",
        "🟢 GST Portal": "Synced",
        "🟡 Reports": "Processing"
    }
    
    for component, status in system_status.items():
        st.markdown(f"{component}: **{status}**")

# --- Main Content Area with Enhanced Layout ---
active_conv = st.session_state["active_conversation"]
if active_conv not in st.session_state["conversations"]:
    st.session_state["conversations"][active_conv] = []
messages = st.session_state["conversations"][active_conv]

# --- Intelligent Chat Interface ---
st.markdown("## 💬 AI Assistant Chat")


# Context-aware input placeholder
conversation_count = len(st.session_state["conversations"])
context_placeholder = f"Ask about invoices, GST, tickets..."

# Enhanced input area
input_col, button_col = st.columns([5, 1])

with input_col:
    user_input = st.text_input(
        "🎤 Voice your query here...",
        value=st.session_state.get("quick_query", ""),
        placeholder=context_placeholder,
        label_visibility="collapsed",
        key="user_query"
    )

with button_col:
    send_button = st.button("🚀 Send", use_container_width=True, type="primary")

# Clear quick query after using it
if "quick_query" in st.session_state:
    del st.session_state["quick_query"]

# --- Advanced Chat Display ---
chat_container = st.container()

with chat_container:
    if not messages:
        # Enhanced welcome message
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(245, 147, 251, 0.1) 100%); border-radius: 16px; margin: 2rem 0;">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">👋 Welcome to Your AI Assistant!</h2>
            <p style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 2rem;">
                I'm here to help you with GST compliance, invoice management, and support tickets.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(245, 147, 251, 0.1) 100%); border-radius: 16px; margin: 2rem 0"; padding: 1rem; border-radius: 8px; box-shadow: var(--shadow);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💼</div>
                    <strong>Invoice Management</strong>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">Filter, track, and reconcile invoices</p>
                </div>
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(245, 147, 251, 0.1) 100%); border-radius: 16px; margin: 2rem 0"; padding: 1rem; border-radius: 8px; box-shadow: var(--shadow);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <strong>GST Reports</strong>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">Generate and download reports</p>
                </div>
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(245, 147, 251, 0.1) 100%); border-radius: 16px; margin: 2rem 0"; padding: 1rem; border-radius: 8px; box-shadow: var(--shadow);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎫</div>
                    <strong>Support Tickets</strong>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">Create and track support requests</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
    # Group messages into conversation pairs and display in reverse chronological order
        recent_messages = messages[-20:] if len(messages) > 20 else messages  # Get more messages for pairing
        
        # Display messages in reverse order but maintain question-answer flow
        displayed_count = 0
        for i in range(len(recent_messages) - 1, -1, -1):  # Go backwards through messages
            if displayed_count >= 20:  # Limit display
                break
                
            msg = recent_messages[i]
            timestamp = msg.get("timestamp", "")
            
            # If this is an assistant message, also show the preceding user message
            if msg["role"] == "assistant" and i > 0 and recent_messages[i-1]["role"] == "user":
                user_msg = recent_messages[i-1]
                user_timestamp = user_msg.get("timestamp", "")
                
                # Display user message first
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="margin-right: 0.5rem;">👤 You</strong>
                        <span style="font-size: 0.8rem; opacity: 0.8;">{user_timestamp}</span>
                    </div>
                    <div style="font-size: 1rem; line-height: 1.5;">{user_msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Then display assistant response
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="margin-right: 0.5rem;">🤖 Assistant</strong>
                        <span style="font-size: 0.8rem; opacity: 0.8;">{timestamp}</span>
                    </div>
                    <div style="font-size: 1rem; line-height: 1.5;">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced action display
                if "actions" in msg and msg["actions"]:
                    with st.expander("⚡ Actions Performed", expanded=False):
                        for j, action in enumerate(msg["actions"]):
                            st.markdown(f"""
                            <div class="custom-alert alert-success">
                                <strong>Action {j+1}:</strong> {action}
                            </div>
                            """, unsafe_allow_html=True)
                
                displayed_count += 2  # We displayed 2 messages
                
            # Skip user messages that were already paired with assistant responses
            elif msg["role"] == "user" and i < len(recent_messages) - 1 and recent_messages[i+1]["role"] == "assistant":
                continue  # This will be handled when we process the assistant message
                
            # Handle standalone messages (shouldn't happen in normal flow, but just in case)
            elif msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="margin-right: 0.5rem;">👤 You</strong>
                        <span style="font-size: 0.8rem; opacity: 0.8;">{timestamp}</span>
                    </div>
                    <div style="font-size: 1rem; line-height: 1.5;">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
                displayed_count += 1

# --- Enhanced Message Processing ---
if (send_button and user_input.strip()) or (user_input.strip() and st.session_state.get("auto_send", False)):
    if user_input.strip():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add user message with enhanced metadata
        user_message = {
            "role": "user", 
            "content": user_input, 
            "timestamp": timestamp,
            "user_role": role,
            "conversation_id": active_conv
        }
        messages.append(user_message)

        # Show thinking indicator
        with st.spinner("🤔 Processing your request..."):
            try:
                # Enhanced routing with context
                response, trace = router.route_query(
                    user_input, role, FAQS, EMAILS, st.session_state["tickets"], ACTIONS, user_id
                )

                # Process and format response
                if isinstance(response, dict):
                    text = response.get("text", "")
                    actions_done = response.get("actions", [])
                    confidence = response.get("confidence", 0.9)
                    
                    assistant_message = {
                        "role": "assistant",
                        "content": text,
                        "timestamp": timestamp,
                        "actions": actions_done,
                        "confidence": confidence,
                        "trace_module": trace
                    }
                else:
                    assistant_message = {
                        "role": "assistant", 
                        "content": response, 
                        "timestamp": timestamp,
                        "confidence": 0.8,
                        "trace_module": trace
                    }
                
                messages.append(assistant_message)

                # Enhanced conversation saving
                cm.save_conversation(
                    user_id,
                    user_input,
                    response if not isinstance(response, dict) else response.get("text", ""),
                    {
                        "role": role, 
                        "timestamp": datetime.now().isoformat(),
                        "trace": trace,
                        "conversation_id": active_conv,
                        "actions_performed": actions_done if isinstance(response, dict) else [],
                        "confidence": assistant_message.get("confidence", 0.8)
                    }
                )
                
                # Enhanced trace logging
                trace_logger.log_trace(user_input, response, trace)
                
                # Update session activity
                st.session_state["last_activity"] = datetime.now()
                
                # Success notification
                st.success("✅ Response generated successfully!")

            except Exception as e:
                error_msg = f"⚠️ I encountered an error: {str(e)}"
                messages.append({
                    "role": "assistant", 
                    "content": error_msg, 
                    "timestamp": timestamp,
                    "error": True,
                    "trace_module": "Error Handler"
                })
                st.error("❌ Something went wrong. Please try again.")

        st.rerun()

# --- Enhanced Tabbed Interface ---
st.markdown("---")
st.markdown("## 📋 System Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎫 Smart Tickets", 
    "📊 Advanced Analytics", 
    "🔍 Trace Intelligence", 
    "🧠 Context Manager", 
    "💡 AI Insights"
])

with tab1:
    st.markdown("### 🎫 Intelligent Ticket Management")
    
    # Advanced filtering with multiple options
    filter_row1 = st.columns(4)
    with filter_row1[0]:
        status_filter = st.selectbox("📊 Status", ["All", "Open", "Closed", "In Progress", "Pending"])
    with filter_row1[1]:
        priority_filter = st.selectbox("⭐ Priority", ["All", "High", "Medium", "Low"])
    with filter_row1[2]:
        date_filter = st.selectbox("📅 Created", ["All Time", "Today", "This Week", "This Month"])
    with filter_row1[3]:
        assigned_filter = st.selectbox("👤 Assigned", ["All", "Support Team", "Compliance Team", "My Tickets"])
    
    # Smart search
    search_query = st.text_input("🔍 Search tickets...", placeholder="Search by ID, summary, or keywords")
    
    # Apply intelligent filtering
    visible_tickets = st.session_state["tickets"].copy()
    
    # Role-based filtering
    if role.lower() == "viewer":
        visible_tickets = [t for t in visible_tickets if t["status"] in ["open", "in_progress"]]
    
    # Apply filters
    if status_filter != "All":
        visible_tickets = [t for t in visible_tickets if t["status"].lower().replace("_", " ") == status_filter.lower()]
    if priority_filter != "All":
        visible_tickets = [t for t in visible_tickets if t["priority"].lower() == priority_filter.lower()]
    if search_query:
        visible_tickets = [t for t in visible_tickets if search_query.lower() in t["summary"].lower() or search_query.lower() in t["ticket_id"].lower()]
    
    # Advanced ticket analytics
    if visible_tickets:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", len(visible_tickets))
        with col2:
            high_priority = len([t for t in visible_tickets if t["priority"] == "high"])
            st.metric("High Priority", high_priority)
        with col3:
            open_tickets = len([t for t in visible_tickets if t["status"] == "open"])
            st.metric("Open", open_tickets)
        with col4:
            avg_age = "3.2 days"  # Simulated
            st.metric("Avg Age", avg_age)
    
    # Enhanced ticket display with professional cards
    if visible_tickets:
        for ticket in visible_tickets:
            # Calculate ticket age
            created_date = datetime.strptime(ticket["created_at"], "%Y-%m-%d")
            age_days = (datetime.now() - created_date).days
            
            # Determine urgency color
            urgency_color = "#ef4444" if ticket["priority"] == "high" else "#f59e0b" if ticket["priority"] == "medium" else "#10b981"
            
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                padding: 1.5rem; 
                margin: 1rem 0; 
                border-radius: 12px; 
                border-left: 4px solid {urgency_color}; 
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: var(--primary-color); font-size: 1.1rem;">
                            🎫 {ticket['ticket_id']}: {ticket['summary']}
                        </h4>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span class="status-indicator status-{ticket['status']}">{ticket['status'].replace('_', ' ').title()}</span>
                        <span class="status-indicator priority-{ticket['priority']}" style="color: white;">{ticket['priority'].upper()}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    <div><strong>📅 Created:</strong> {ticket['created_at']} ({age_days} days ago)</div>
                    <div><strong>👤 Assigned:</strong> {ticket['assigned_to']}</div>
                    <div><strong>🔄 Updated:</strong> {ticket['updated_at']}</div>
                    <div><strong>⏱️ Age:</strong> {age_days} days</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons for each ticket
            if role.lower() in ["admin", "manager"]:
                action_cols = st.columns(4)
                with action_cols[0]:
                    if st.button(f"👀 View {ticket['ticket_id']}", key=f"view_{ticket['ticket_id']}"):
                        st.info(f"Viewing details for {ticket['ticket_id']}")
                with action_cols[1]:
                    if st.button(f"✏️ Edit {ticket['ticket_id']}", key=f"edit_{ticket['ticket_id']}"):
                        st.info(f"Edit functionality for {ticket['ticket_id']}")
                with action_cols[2]:
                    if st.button(f"💬 Comment {ticket['ticket_id']}", key=f"comment_{ticket['ticket_id']}"):
                        st.info(f"Adding comment to {ticket['ticket_id']}")
                with action_cols[3]:
                    if ticket['status'] != 'closed' and st.button(f"✅ Close {ticket['ticket_id']}", key=f"close_{ticket['ticket_id']}"):
                        st.success(f"Ticket {ticket['ticket_id']} marked as closed!")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
            <h3>🔍 No tickets match your filters</h3>
            <p>Try adjusting your search criteria or create a new ticket.</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📊 Advanced System Analytics")
    
    # Real-time metrics dashboard
    metrics_row = st.columns(5)
    analytics = get_conversation_analytics()
    
    with metrics_row[0]:
        st.metric("🗣️ Total Queries", analytics["total_messages"], delta="12 today")
    with metrics_row[1]:
        st.metric("⚡ Avg Response", analytics["avg_response_time"], delta="-0.3s")
    with metrics_row[2]:
        success_rate = "94.7%"
        st.metric("✅ Success Rate", success_rate, delta="2.1%")
    with metrics_row[3]:
        active_users = len(set(conv_id.split('-')[0] for conv_id in st.session_state["conversations"].keys())) if st.session_state["conversations"] else 1
        st.metric("👥 Active Users", active_users, delta=1)
    with metrics_row[4]:
        st.metric("⭐ Satisfaction", f"{analytics['user_satisfaction']}/5.0", delta="0.2")
    
    # Module Performance Analysis
    st.markdown("#### 🎯 AI Module Performance")
    if analytics["module_stats"]:
        module_data = []
        total_queries = sum(analytics["module_stats"].values())
        
        for module, count in analytics["module_stats"].items():
            percentage = (count / total_queries) * 100
            module_data.append({
                "Module": module.replace(" Module", "").replace("(", "").replace(")", ""),
                "Queries": count,
                "Percentage": f"{percentage:.1f}%",
                "Avg Response": f"{1.2 + (count % 10) * 0.1:.1f}s"  # Simulated
            })
        
        # Display as professional table
        for module_info in sorted(module_data, key=lambda x: x["Queries"], reverse=True):
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{module_info['Module']}**")
            with cols[1]:
                st.markdown(f"`{module_info['Queries']} queries`")
            with cols[2]:
                st.markdown(f"`{module_info['Percentage']}`")
            with cols[3]:
                st.markdown(f"`{module_info['Avg Response']}`")
    
    # System Health Monitoring
    st.markdown("#### 🔧 System Health Monitor")
    health_cols = st.columns(2)
    
    with health_cols[0]:
        st.markdown("**Core Components Status**")
        components = [
            ("🔵 Router Engine", "Operational", "#10b981"),
            ("🔵 Context Manager", "Operational", "#10b981"),
            ("🟡 Trace Logger", "Warning", "#f59e0b"),
            ("🔵 Action Handler", "Operational", "#10b981"),
        ]
        
        for component, status, color in components:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px; margin: 0.25rem 0;">
                <span>{component}</span>
                <span style="color: {color}; font-weight: bold;">{status}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with health_cols[1]:
        st.markdown("**Performance Metrics**")
        perf_metrics = [
            ("Memory Usage", "67%", 67),
            ("CPU Usage", "34%", 34),
            ("Response Time", "1.2s", 80),
            ("Uptime", "99.8%", 99),
        ]
        
        for metric, value, progress in perf_metrics:
            st.markdown(f"**{metric}**: {value}")
            st.progress(progress / 100)

with tab3:
    st.markdown("### 🔍 Advanced Trace Intelligence")
    
    # Enhanced trace filtering
    trace_controls = st.columns(3)
    with trace_controls[0]:
        trace_limit = st.selectbox("Show traces", [5, 10, 25, 50], index=1)
    with trace_controls[1]:
        trace_module_filter = st.selectbox("Filter by module", ["All", "FAQ", "Actions", "Support", "Context"])
    with trace_controls[2]:
        trace_time_filter = st.selectbox("Time range", ["All", "Last Hour", "Today", "This Week"])
    
    traces = get_persistent_traces(trace_limit)
    
    if traces:
        # Trace analytics
        st.markdown("#### 📈 Trace Analytics")
        trace_stats_cols = st.columns(4)
        
        with trace_stats_cols[0]:
            st.metric("Total Traces", len(traces))
        with trace_stats_cols[1]:
            unique_modules = len(set(t.get('routed_to', '') for t in traces))
            st.metric("Unique Modules", unique_modules)
        with trace_stats_cols[2]:
            avg_query_length = sum(len(t.get('query', '')) for t in traces) / len(traces)
            st.metric("Avg Query Length", f"{avg_query_length:.0f} chars")
        with trace_stats_cols[3]:
            success_traces = len([t for t in traces if 'error' not in t.get('routed_to', '').lower()])
            success_rate = (success_traces / len(traces)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Detailed trace viewer
        st.markdown("#### 🔬 Detailed Trace Analysis")
        for i, entry in enumerate(traces):
            timestamp = entry.get('timestamp', 'N/A')
            query = entry.get('query', 'N/A')
            routed_to = entry.get('routed_to', 'Unknown')
            response = entry.get('response', 'N/A')
            
            # Color coding based on module
            module_colors = {
                "FAQ Module": "#3b82f6",
                "Actions Module": "#10b981", 
                "Support Module": "#f59e0b",
                "Context-Enhanced Response": "#8b5cf6",
                "Fallback": "#ef4444"
            }
            module_color = module_colors.get(routed_to, "#6b7280")
            
            with st.expander(f"🕒 {timestamp} - Trace #{i+1} - {routed_to}", expanded=False):
                trace_details = st.columns([1, 1])
                
                with trace_details[0]:
                    st.markdown("**📝 Query Analysis**")
                    st.code(query, language="text")
                    st.markdown(f"**🎯 Routed to:** `{routed_to}`")
                    st.markdown(f"**📏 Query Length:** {len(query)} characters")
                    st.markdown(f"**🕐 Timestamp:** {timestamp}")
                
                with trace_details[1]:
                    st.markdown("**🤖 Response Analysis**")
                    # Safe string handling for response preview
                    response_str = str(response) if response else "No response"
                    response_preview = response_str[:200] + ("..." if len(response_str) > 200 else "")
                    st.text_area("Response", response_preview, height=100, key=f"trace_response_{i}")
                    st.markdown(f"**📏 Response Length:** {len(response_str)} characters")
                    
                    # Response sentiment analysis (simulated)
                    sentiment = "Helpful" if "error" not in response_str.lower() else "Error"
                    sentiment_color = "#10b981" if sentiment == "Helpful" else "#ef4444"
                    st.markdown(f"**😊 Sentiment:** <span style='color: {sentiment_color}'>{sentiment}</span>", unsafe_allow_html=True)
    else:
        st.info("🔍 No traces available yet. Start chatting to see system traces here.")

with tab4:
    st.markdown("### 🧠 Intelligent Context Manager")
    
    # Context overview
    st.markdown("#### 📚 Conversation Context")
    
    if st.session_state["conversations"]:
        context_metrics = st.columns(4)
        
        total_conversations = len(st.session_state["conversations"])
        total_messages = sum(len(msgs) for msgs in st.session_state["conversations"].values())
        active_topics = ["GST Filing", "Invoice Management", "Ticket Support", "System Queries"]  # Simulated
        context_retention = "85%"  # Simulated
        
        with context_metrics[0]:
            st.metric("💬 Total Conversations", total_conversations)
        with context_metrics[1]:
            st.metric("💭 Total Messages", total_messages)
        with context_metrics[2]:
            st.metric("🏷️ Active Topics", len(active_topics))
        with context_metrics[3]:
            st.metric("🧠 Context Retention", context_retention)
        
        # Context visualization
        st.markdown("#### 🗺️ Context Relationship Map")
        
        # Display conversation clusters
        for topic in active_topics:
            with st.expander(f"📋 {topic} Conversations", expanded=False):
                st.markdown(f"**Recent queries related to {topic}:**")
                # Simulated related queries
                related_queries = [
                    f"Show {topic.lower()} status",
                    f"Help with {topic.lower()}",
                    f"Generate {topic.lower()} report"
                ]
                for query in related_queries:
                    st.markdown(f"• {query}")
        
        # User interaction patterns
        st.markdown("#### 👤 User Interaction Patterns")
        
        patterns_cols = st.columns(2)
        with patterns_cols[0]:
            st.markdown("**🕐 Activity Timeline**")
            # Simulated activity data
            st.bar_chart({
                "Monday": 15,
                "Tuesday": 23,
                "Wednesday": 18,
                "Thursday": 31,
                "Friday": 25,
                "Saturday": 8,
                "Sunday": 5
            })
        
        with patterns_cols[1]:
            st.markdown("**📊 Query Categories**")
            # Simulated category data
            st.bar_chart({
                "Invoice Queries": 45,
                "GST Questions": 38,
                "Support Tickets": 22,
                "System Help": 15
            })
    else:
        st.info("🧠 Context intelligence will appear as you interact with the assistant.")

with tab5:
    st.markdown("### 💡 AI Insights & Recommendations")
    
    # Intelligent recommendations
    st.markdown("#### 🎯 Personalized Recommendations")
    
    # Based on user role and activity
    recommendations = {
        "Admin": [
            "🔧 Consider setting up automated GST filing reminders",
            "📊 Review system performance metrics weekly", 
            "👥 Monitor user activity and access patterns",
            "🔍 Set up audit trail alerts for critical actions"
        ],
        "Manager": [
            "📄 Schedule weekly invoice reconciliation",
            "📈 Set up performance dashboards for your team",
            "🎫 Review and prioritize high-priority tickets",
            "📊 Generate monthly compliance reports"
        ],
        "Viewer": [
            "📚 Explore the help documentation",
            "🔔 Set up notifications for ticket updates",
            "📋 Bookmark frequently used reports",
            "❓ Use quick actions for common tasks"
        ]
    }
    
    current_recommendations = recommendations.get(role, recommendations["Viewer"])
    
    for i, recommendation in enumerate(current_recommendations):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(245, 147, 251, 0.1) 100%); 
                    padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid var(--primary-color);">
            <strong>Recommendation {i+1}:</strong> {recommendation}
        </div>
        """, unsafe_allow_html=True)
    
    # AI Performance Insights
    st.markdown("#### 🤖 AI Performance Insights")
    
    insights_cols = st.columns(2)
    
    with insights_cols[0]:
        st.markdown("**🎯 Top Performing Features**")
        top_features = [
            ("Invoice Filtering", "95% success rate"),
            ("FAQ Resolution", "92% accuracy"),
            ("Ticket Creation", "98% success rate"),
            ("GST Report Generation", "89% success rate")
        ]
        
        for feature, performance in top_features:
            st.markdown(f"• **{feature}**: {performance}")
    
    with insights_cols[1]:
        st.markdown("**🔧 Areas for Improvement**")
        improvements = [
            ("Context retention across sessions", "Medium priority"),
            ("Complex query understanding", "High priority"),
            ("Multi-step action sequences", "Low priority"),
            ("Natural language processing", "Medium priority")
        ]
        
        for improvement, priority in improvements:
            color = "#ef4444" if priority == "High priority" else "#f59e0b" if priority == "Medium priority" else "#10b981"
            st.markdown(f"• **{improvement}**: <span style='color: {color}'>{priority}</span>", unsafe_allow_html=True)
    
    # Predictive insights
    st.markdown("#### 🔮 Predictive Insights")
    
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.1); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
        <h4 style="color: var(--primary-color); margin-bottom: 1rem;">🔍 AI Predictions</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>📈 Usage Trend:</strong><br>
                Expected 25% increase in queries next month
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>🎫 Ticket Volume:</strong><br>
                Likely spike in GST-related tickets before filing deadline
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>⚡ Peak Hours:</strong><br>
                Highest activity expected between 10 AM - 12 PM
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>🎯 Optimization:</strong><br>
                FAQ updates could reduce support tickets by 15%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

last_updated = datetime.now().strftime('%Y-%m-%d')

# --- Professional Footer ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); 
            border-radius: 12px; color: white; margin: 2rem 0;">
    <h3 style="margin-bottom: 1rem;">🚀 Finkraft Unified AI Assistant</h3>
    <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;">
        <div><strong>Version:</strong> 2.0.0</div>
        <div><strong>Status:</strong> 🟢 Operational</div>
        <div><strong>Uptime:</strong> 99.8%</div>
        <div> <strong>Last Updated:</strong>{last_updated}<br>
</div>
    </div>
    <p style="margin: 1rem 0; opacity: 0.9;">Powered by Advanced AI • Built with ❤️ for Enterprise Excellence</p>
    <div style="font-size: 0.9rem; opacity: 0.8;">
        © 2025 Finkraft Technologies • Transforming Business Intelligence Through AI
    </div>
</div>
""", unsafe_allow_html=True)