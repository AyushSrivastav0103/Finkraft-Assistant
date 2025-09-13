import re
import json
import os
from datetime import datetime

# Load action configuration
def load_action_config():
    config_path = os.path.join("config", "actions_config.json")
    with open(config_path, "r") as f:
        return json.load(f)

# Example action handlers — these should later connect to real services
def filter_invoices(query, role, params=None):
    # Extract parameters from query
    date_range = None
    vendor = None
    status = None
    
    # Simple parameter extraction (in a real system, use NLP)
    if "last month" in query:
        date_range = "last month"
    elif "this month" in query:
        date_range = "this month"
    
    if "pending" in query:
        status = "pending"
    elif "failed" in query:
        status = "failed"
    elif "reconciled" in query:
        status = "reconciled"
    
    # Extract vendor name (simple implementation)
    vendor_match = re.search(r"from\s+([A-Za-z\s]+)", query)
    if vendor_match:
        vendor = vendor_match.group(1).strip()
    
    # Simulated example (in real case, filter from DB)
    sample_result = [
        {"invoice_id": "INV-1001", "vendor": "IndiSky", "status": "failed", "date": "2025-08-01"},
        {"invoice_id": "INV-1002", "vendor": "IndiSky", "status": "failed", "date": "2025-08-15"}
    ]
    
    # Format response message
    filter_details = []
    if date_range:
        filter_details.append(f"period: {date_range}")
    if vendor:
        filter_details.append(f"vendor: {vendor}")
    if status:
        filter_details.append(f"status: {status}")
    
    filter_text = ", ".join(filter_details) if filter_details else "your criteria"
    
    return {
        "text": f"Found {len(sample_result)} invoices matching {filter_text}:\n\n" + 
               "\n".join([f"- {inv['invoice_id']}: {inv['vendor']} ({inv['status']}) from {inv['date']}" for inv in sample_result]),
        "actions": [f"Filtered invoices by {filter_text}"]
    }

def download_gst_report(query, role, params=None):
    # Extract period from query
    period = "current month"
    if "last month" in query:
        period = "last month"
    elif "q1" in query.lower() or "quarter 1" in query.lower():
        period = "Q1 2025"
    
    # Simulated file path or URL
    report_path = f"reports/gst_report_{period.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return {
        "text": f"📊 GST report for {period} has been generated and is ready for download.\n\nFile: {report_path}",
        "actions": [f"Generated GST report for {period}"]
    }

def view_filing_status(query, role, params=None):
    # Extract period from query
    period = "current month"
    if "last month" in query:
        period = "last month"
    elif "q1" in query.lower() or "quarter 1" in query.lower():
        period = "Q1 2025"
    
    # Simulated status
    status = "Filed on time"
    if "last month" in query:
        status = "Filed with 2 day delay"
    
    return {
        "text": f"📝 Filing status for {period}: {status}\n\nDetails:\n- Due date: 20th of month\n- Filed date: 22nd of month\n- Status: Complete",
        "actions": [f"Checked filing status for {period}"]
    }

def reconcile_invoices(query, role, params=None):
    # Extract period from query
    period = "current month"
    if "last month" in query:
        period = "last month"
    
    # Simulated reconciliation results
    matched = 42
    mismatched = 3
    missing = 1
    
    return {
        "text": f"🔄 Reconciliation complete for {period}:\n\n- Matched: {matched} invoices\n- Mismatched: {mismatched} invoices\n- Missing from GSTR-2A: {missing} invoice",
        "actions": [f"Reconciled invoices for {period}"]
    }

def raise_ticket(query, role, params=None):
    # Extract priority from query
    priority = "medium"
    if "urgent" in query or "high priority" in query:
        priority = "high"
    elif "low priority" in query:
        priority = "low"
    
    ticket_id = f"TCK-{datetime.now().strftime('%H%M%S')}"
    
    return {
        "text": f"✅ Ticket {ticket_id} created with {priority} priority for: {query}",
        "actions": [f"Created ticket {ticket_id} with {priority} priority"]
    }

# Action mapping
ACTION_HANDLERS = {
    "filter_invoices": filter_invoices,
    "download_gst_report": download_gst_report,
    "view_filing_status": view_filing_status,
    "reconcile_invoices": reconcile_invoices,
    "raise_ticket": raise_ticket
}

# Action patterns for matching
ACTION_PATTERNS = {
    "filter_invoices": ["filter invoices", "show invoices", "find invoices", "search invoices"],
    "download_gst_report": ["download report", "get report", "generate report", "export report"],
    "view_filing_status": ["filing status", "check status", "gst status"],
    "reconcile_invoices": ["reconcile", "match invoices", "compare invoices"],
    "raise_ticket": ["raise ticket", "create ticket", "new ticket", "open ticket"]
}

def handle_action(query: str, role: str):
    """
    Match query against config-driven actions and return structured result.
    """
    query_lower = query.lower()
    
    # Check if user has permission for actions
    action_config = load_action_config()
    allowed_actions = [a["name"] for a in action_config if role.lower() in [r.lower() for r in a["role_access"]]]
    
    # Match query against action patterns
    for action_name, patterns in ACTION_PATTERNS.items():
        if action_name not in allowed_actions:
            continue
            
        if any(pattern in query_lower for pattern in patterns):
            handler = ACTION_HANDLERS.get(action_name)
            if handler:
                return handler(query, role)
    
    return None
