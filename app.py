import streamlit as st
import json
import uuid
from datetime import datetime

# Core modules
from core import router
from core import context_manager as cm
from utils.role_manager import get_allowed_actions
from utils import trace_logger
from utils.trace_logger import get_persistent_traces

# --- Load Data ---
def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

FAQS = load_json("data/faqs.json")
EMAILS = load_json("data/sample_emails.json")
ACTIONS = load_json("config/actions_config.json")
TICKETS = load_json("data/tickets.json")

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Finkraft Unified Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Finkraft Unified In-App Assistant")

# --- Sidebar: Role Selection ---
role = st.sidebar.selectbox(
    "Select Role",
    ["Admin", "Manager", "Viewer"],
    index=0
)
st.sidebar.write(f"🔑 Current role: **{role}**")

# --- Session State ---
if "conversations" not in st.session_state:
    st.session_state["conversations"] = {}  # {conv_id: [messages]}
if "active_conversation" not in st.session_state:
    st.session_state["active_conversation"] = str(uuid.uuid4())
if "tickets" not in st.session_state:
    st.session_state["tickets"] = TICKETS
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

user_id = st.session_state["user_id"]

# --- Sidebar: Conversations ---
st.sidebar.subheader("💬 Conversations")

if st.sidebar.button("➕ New Conversation"):
    st.session_state["active_conversation"] = str(uuid.uuid4())

# End conversation (resets active conversation)
if st.sidebar.button("🛑 End Conversation"):
    conv_id = st.session_state["active_conversation"]
    # Archive conversation in DB before resetting
    if conv_id in st.session_state["conversations"]:
        cm.save_conversation(
            user_id,
            "Conversation Ended",
            "User ended conversation",
            {"role": role, "timestamp": str(datetime.now()), "trace": {}},
        )
    st.session_state["active_conversation"] = str(uuid.uuid4())

# Show existing conversations
for conv_id, msgs in st.session_state["conversations"].items():
    if msgs:
        title = msgs[0]["content"][:30] + ("..." if len(msgs[0]["content"]) > 30 else "")
    else:
        title = "(empty)"
    if st.sidebar.button(title, key=f"conv-{conv_id}"):
        st.session_state["active_conversation"] = conv_id

# Get active messages
active_conv = st.session_state["active_conversation"]
if active_conv not in st.session_state["conversations"]:
    st.session_state["conversations"][active_conv] = []
messages = st.session_state["conversations"][active_conv]

# --- Chat UI ---
st.subheader("💬 Chat with Assistant")

user_input = st.text_input("Type your query:", "")

chat_container = st.container()
with chat_container:
    to_display = messages[-10:] if len(messages) > 10 else messages
    for msg in to_display:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
                if "actions" in msg:
                    with st.expander("⚡ Actions executed"):
                        for act in msg["actions"]:
                            st.write(f"- {act}")

if st.button("Send") and user_input.strip():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.append({"role": "user", "content": user_input, "timestamp": timestamp})

    try:
        response, trace = router.route_query(
            user_input, role, FAQS, EMAILS, st.session_state["tickets"], ACTIONS, user_id
        )

        if isinstance(response, dict):
            text = response.get("text", "")
            actions_done = response.get("actions", [])
            messages.append(
                {
                    "role": "assistant",
                    "content": text,
                    "timestamp": timestamp,
                    "actions": actions_done,
                }
            )
        else:
            messages.append(
                {"role": "assistant", "content": response, "timestamp": timestamp}
            )

        cm.save_conversation(
            user_id,
            user_input,
            response if not isinstance(response, dict) else response.get("text", ""),
            {"role": role, "timestamp": str(datetime.now()), "trace": trace},
        )
        trace_logger.log_trace(user_input, response, trace)

        st.experimental_rerun()

    except Exception as e:
        messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})

# --- Context Tabs ---
tabs = st.tabs(["📂 Tickets", "⚡ Allowed Actions", "🔍 Trace Viewer"])

with tabs[0]:
    st.write("### Open Tickets")
    visible_tickets = (
        [t for t in st.session_state["tickets"] if t["status"] != "closed"]
        if role.lower() == "viewer"
        else st.session_state["tickets"]
    )
    for t in visible_tickets:
        st.write(
            f"**{t['ticket_id']}** - {t['summary']} ({t['status']}, Priority: {t['priority']})"
        )

with tabs[1]:
    st.write("### Allowed Actions")
    allowed_actions = get_allowed_actions(role, ACTIONS)
    for action in allowed_actions:
        st.write(f"- {action['name']}: {action['description']}")

with tabs[2]:
    st.write("### Recent Traces")
    traces = get_persistent_traces(5)
    if traces:
        for entry in traces:
            with st.expander(f"🕒 {entry['timestamp']} - {entry['query'][:30]}..."):
                st.write(f"**Query:** {entry['query']}")
                st.write(f"**Response:** {entry['response']}")
                st.write(f"**Handled by:** {entry['routed_to']}")
    else:
        st.write("No traces available yet. Start a conversation to see traces.")

# --- Sidebar Quick Prompts ---
st.sidebar.subheader("💡 Try asking:")
st.sidebar.write("- Filter invoices from last month")
st.sidebar.write("- Download GST report for Q1")
st.sidebar.write("- Why did my GST filing fail?")
st.sidebar.write("- Create a ticket for invoice mismatch")
st.sidebar.write("- Check filing status for last month")
