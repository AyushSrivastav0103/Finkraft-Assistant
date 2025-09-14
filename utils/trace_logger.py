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
        os.makedirs(os.path.dirname(TRACE_LOG_PATH), exist_ok=True)
        with open(TRACE_LOG_PATH, "w") as f:
            json.dump([], f)

# --- Core Functions ---

def log_trace(query, response, module, metadata=None):
    """
    Log a trace entry to both session state and file.
    
    Args:
        query (str): The user query
        response (str/dict): The response from the system
        module (str): The module that handled the query
        metadata (dict, optional): Additional metadata about the trace
    """
    ensure_trace_logs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Handle response formatting safely
    if isinstance(response, dict):
        response_text = str(response.get('text', response))
    else:
        response_text = str(response)
    
    # Truncate long responses for storage
    if len(response_text) > 200:
        display_response = response_text[:200] + "..."
    else:
        display_response = response_text

    # Create enhanced trace entry
    trace_entry = {
        "timestamp": timestamp,
        "query": query,
        "response": display_response,
        "routed_to": module,
    }
    
    # Add metadata if provided
    if metadata:
        trace_entry.update({
            "confidence": metadata.get("confidence", 0.5),
            "complexity": metadata.get("complexity", "unknown"),
            "context_used": metadata.get("context_used", False),
            "user_context": metadata.get("user_context_summary", {}),
            "execution_time": metadata.get("execution_time", "N/A")
        })

    # Add to session state
    st.session_state["trace_logs"].append(trace_entry)

    # Save to persistent file
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

def get_trace_analytics():
    """Get analytics about system performance from traces."""
    traces = get_persistent_traces(100)  # Get more traces for analysis
    
    if not traces:
        return {
            "total_traces": 0,
            "modules_used": {},
            "average_confidence": 0.0,
            "context_usage_rate": 0.0
        }
    
    # Analyze trace data
    modules_used = {}
    confidence_scores = []
    context_used_count = 0
    
    for trace in traces:
        # Count module usage
        module = trace.get("routed_to", "Unknown")
        modules_used[module] = modules_used.get(module, 0) + 1
        
        # Collect confidence scores
        confidence = trace.get("confidence", 0.5)
        confidence_scores.append(confidence)
        
        # Count context usage
        if trace.get("context_used", False):
            context_used_count += 1
    
    # Calculate metrics
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    context_usage_rate = (context_used_count / len(traces)) * 100 if traces else 0.0
    
    return {
        "total_traces": len(traces),
        "modules_used": modules_used,
        "average_confidence": round(avg_confidence, 2),
        "context_usage_rate": round(context_usage_rate, 1),
        "most_used_module": max(modules_used.items(), key=lambda x: x[1])[0] if modules_used else "None"
    }

def search_traces(search_term, limit=10):
    """Search through trace history for specific terms."""
    traces = get_persistent_traces(50)  # Search through more traces
    
    if not search_term:
        return traces[:limit]
    
    search_lower = search_term.lower()
    matching_traces = []
    
    for trace in traces:
        # Check if search term appears in query or response
        if (search_lower in trace.get("query", "").lower() or 
            search_lower in trace.get("response", "").lower() or
            search_lower in trace.get("routed_to", "").lower()):
            matching_traces.append(trace)
    
    return matching_traces[:limit]

def get_module_performance(module_name):
    """Get performance statistics for a specific module."""
    traces = get_persistent_traces(100)
    
    module_traces = [t for t in traces if t.get("routed_to") == module_name]
    
    if not module_traces:
        return {
            "module": module_name,
            "total_queries": 0,
            "average_confidence": 0.0,
            "recent_queries": []
        }
    
    # Calculate statistics
    confidence_scores = [t.get("confidence", 0.5) for t in module_traces]
    avg_confidence = sum(confidence_scores) / len(confidence_scores)
    
    # Get recent queries (last 5)
    recent_queries = [
        {
            "query": t.get("query", ""),
            "confidence": t.get("confidence", 0.5),
            "timestamp": t.get("timestamp", "")
        }
        for t in module_traces[-5:]
    ]
    
    return {
        "module": module_name,
        "total_queries": len(module_traces),
        "average_confidence": round(avg_confidence, 2),
        "recent_queries": recent_queries
    }

def export_traces_csv():
    """Export traces to CSV format (returns CSV string)."""
    traces = get_persistent_traces(100)
    
    if not traces:
        return "No traces available for export"
    
    # CSV header
    csv_content = "Timestamp,Query,Response,Module,Confidence,Context Used\n"
    
    # CSV rows
    for trace in traces:
        timestamp = trace.get("timestamp", "")
        query = trace.get("query", "").replace(",", ";")  # Replace commas to avoid CSV issues
        response = trace.get("response", "").replace(",", ";")[:100]  # Truncate and replace commas
        module = trace.get("routed_to", "")
        confidence = trace.get("confidence", "N/A")
        context_used = trace.get("context_used", False)
        
        csv_content += f'"{timestamp}","{query}","{response}","{module}",{confidence},{context_used}\n'
    
    return csv_content

# Backward compatibility - keep the old function signature working
def log_simple_trace(query, response, module):
    """Simple trace logging for backward compatibility."""
    log_trace(query, response, module)