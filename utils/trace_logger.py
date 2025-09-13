import streamlit as st
import json
import os
from datetime import datetime

# Initialize trace logs in session state
if "trace_logs" not in st.session_state:
    st.session_state["trace_logs"] = []

# Path for persistent trace logs
TRACE_LOG_PATH = os.path.join("data", "trace_log.json")

# Initialize trace log file if it doesn't exist
def initialize_trace_file():
    if not os.path.exists(TRACE_LOG_PATH):
        with open(TRACE_LOG_PATH, "w") as f:
            json.dump([], f)

# Log trace to both session state and file
def log_trace(query, response, module):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create trace entry
    trace_entry = {
        "timestamp": timestamp,
        "query": query,
        "response": response[:100] + "..." if len(response) > 100 else response,
        "routed_to": module
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
        print(f"Error saving trace log: {str(e)}")

# Get traces from session state
def get_traces(limit=10):
    return st.session_state["trace_logs"][-limit:]

# Get traces from file
def get_persistent_traces(limit=10):
    initialize_trace_file()
    try:
        with open(TRACE_LOG_PATH, "r") as f:
            traces = json.load(f)
        return traces[-limit:]
    except Exception as e:
        print(f"Error reading trace log: {str(e)}")
        return []
