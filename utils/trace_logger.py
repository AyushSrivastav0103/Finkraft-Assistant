import streamlit as st
import json
import os
from datetime import datetime

# Path for persistent trace logs
TRACE_LOG_PATH = os.path.join("data", "trace_log.json")

# --- Helpers ---

def ensure_trace_logs():
    """Make sure trace_logs always exists in session_state."""
    if "trace_logs" not in st.session_state:
        st.session_state["trace_logs"] = []

def initialize_trace_file():
    """Initialize the persistent trace log file if it doesn't exist."""
    if not os.path.exists(TRACE_LOG_PATH):
        with open(TRACE_LOG_PATH, "w") as f:
            json.dump([], f)

# --- Core Functions ---

def log_trace(query, response, module):
    """Log a trace entry to both session state and file."""
    ensure_trace_logs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create trace entry
    trace_entry = {
        "timestamp": timestamp,
        "query": query,
        "response": response[:100] + "..." if isinstance(response, str) and len(response) > 100 else response,
        "routed_to": module,
    }

    # Add to session state
    st.session_state["trace_logs"].append(trace_entry)

    # Save to file
    initialize_trace_file()
    try:
        with open(TRACE_LOG_PATH, "r") as f:
            traces = json.load(f)

        traces.append(trace_entry)

        # Keep only last 100 traces
        if len(traces) > 100:
            traces = traces[-100:]

        with open(TRACE_LOG_PATH, "w") as f:
            json.dump(traces, f, indent=2)

    except Exception as e:
        print(f"⚠️ Error saving trace log: {str(e)}")

def get_traces(limit=10):
    """Get recent traces from session state."""
    ensure_trace_logs()
    return st.session_state["trace_logs"][-limit:]

def get_persistent_traces(limit=10):
    """Get recent traces from the persistent file."""
    initialize_trace_file()
    try:
        with open(TRACE_LOG_PATH, "r") as f:
            traces = json.load(f)
        return traces[-limit:]
    except Exception as e:
        print(f"⚠️ Error reading trace log: {str(e)}")
        return []
