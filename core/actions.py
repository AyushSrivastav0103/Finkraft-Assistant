import re
import json
import os
from datetime import datetime

# Enhanced parameter extraction
# def extract_parameters(query):
#     """Extract structured parameters from natural language query"""
#     params = {}
#     query_lower = query.lower()
    
#     # Extract vendor with multiple patterns
#     vendor_patterns = [
#         r"vendor[=\s]+['\"]?([^'\"]+)['\"]?",
#         r"from\s+([A-Za-z\s]+?)(?:\s|,|$)",
#         r"supplier[=\s]+['\"]?([^'\"]+)['\"]?"
#     ]
    
#     for pattern in vendor_patterns:
#         match = re.search(pattern, query, re.IGNORECASE)
#         if match:
#             params['vendor'] = match.group(1).strip()
#             break
    
#     # Extract status with exact matching
#     status_patterns = [
#         r"status[=\s]+['\"]?(\w+)['\"]?",
#         r"\b(failed|pending|reconciled|open|closed|processing)\b"
#     ]
    
#     for pattern in status_patterns:
#         match = re.search(pattern, query_lower)
#         if match:
#             params['status'] = match.group(1)
#             break
    
#     # Extract time periods
#     time_patterns = {
#         r"\blast\s+month\b": "last_month",
#         r"\bthis\s+month\b": "this_month", 
#         r"\blast\s+quarter\b": "last_quarter",
#         r"\bq[1-4]\s*20\d{2}\b": lambda m: m.group(0).upper(),
#         r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+20\d{2}\b": lambda m: m.group(0)
#     }
    
#     for pattern, value in time_patterns.items():
#         match = re.search(pattern, query_lower)
#         if match:
#             params['period'] = value(match) if callable(value) else value
#             break
    
#     # Extract priority
#     if any(word in query_lower for word in ["urgent", "high priority", "critical"]):
#         params['priority'] = "high"
#     elif any(word in query_lower for word in ["low priority", "minor"]):
#         params['priority'] = "low"
#     else:
#         params['priority'] = "medium"
    
#     return params

def extract_parameters(query: str) -> dict:
    """Extract structured parameters from natural language query."""
    params = {}
    query_lower = query.lower()

    # ---------- Time Period Extraction (highest priority) ----------
    time_patterns = {
        r"\blast\s+month\b": "last_month",
        r"\bthis\s+month\b": "this_month",
        r"\blast\s+quarter\b": "last_quarter",
        r"\bq[1-4]\s*20\d{2}\b": lambda m: m.group(0).upper(),
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+20\d{2}\b": lambda m: m.group(0)
    }

    for pattern, value in time_patterns.items():
        match = re.search(pattern, query_lower)
        if match:
            params["period"] = value(match) if callable(value) else value
            break  # ✅ Stop at first valid time match

    # ---------- Vendor Extraction (run AFTER period to avoid false capture) ----------
    vendor_patterns = [
        r"vendor[=\s]+['\"]?([A-Za-z0-9\s&]+)['\"]?",      # vendor = IndiSky
        r"supplier[=\s]+['\"]?([A-Za-z0-9\s&]+)['\"]?",    # supplier = TechCorp
        r"\bfrom\s+([A-Z][A-Za-z0-9\s&]+)(?=\s|,|$)"       # from IndiSky
    ]

    for pattern in vendor_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            vendor_name = match.group(1).strip()
            # ✅ Guard against false matches like "from last month"
            if vendor_name.lower() not in ["last month", "this month", "last", "this", "quarter"]:
                params["vendor"] = vendor_name
                break

    # ---------- Status Extraction ----------
    status_patterns = [
        r"status[=\s]+['\"]?(\w+)['\"]?",     # status=pending
        r"\b(failed|pending|reconciled|open|closed|processing)\b"
    ]

    for pattern in status_patterns:
        match = re.search(pattern, query_lower)
        if match:
            params["status"] = match.group(1).lower()
            break

    # ---------- Priority Extraction ----------
    if any(word in query_lower for word in ["urgent", "high priority", "critical"]):
        params["priority"] = "high"
    elif any(word in query_lower for word in ["low priority", "minor"]):
        params["priority"] = "low"
    else:
        params["priority"] = "medium"  # ✅ Default

    return params

# Enhanced filter_invoices with better business logic
def filter_invoices(query, role, params=None):
    # Extract parameters using enhanced extraction
    extracted_params = extract_parameters(query)
    
    # Simulate more realistic data
    sample_invoices = [
        {"invoice_id": "INV-2024-001", "vendor": "IndiSky", "status": "failed", "date": "2024-12-01", "amount": 50000, "error": "Missing GSTIN"},
        {"invoice_id": "INV-2024-002", "vendor": "IndiSky", "status": "failed", "date": "2024-12-05", "amount": 75000, "error": "Invalid HSN code"},
        {"invoice_id": "INV-2024-003", "vendor": "TechCorp", "status": "pending", "date": "2024-12-10", "amount": 120000, "error": None},
        {"invoice_id": "INV-2024-004", "vendor": "DataFlow", "status": "reconciled", "date": "2024-12-15", "amount": 95000, "error": None},
        {"invoice_id": "INV-2024-005", "vendor": "IndiSky", "status": "failed", "date": "2024-12-20", "amount": 60000, "error": "Amount mismatch"}
    ]
    
    # Apply filters
    filtered_invoices = sample_invoices
    filter_applied = []
    
    if extracted_params.get('vendor'):
        vendor = extracted_params['vendor'].lower()
        filtered_invoices = [inv for inv in filtered_invoices if vendor in inv['vendor'].lower()]
        filter_applied.append(f"vendor: {extracted_params['vendor']}")
    
    if extracted_params.get('status'):
        status = extracted_params['status']
        filtered_invoices = [inv for inv in filtered_invoices if inv['status'] == status]
        filter_applied.append(f"status: {status}")
    
    if extracted_params.get('period'):
        period = extracted_params['period']
        if period == "last_month":
            # Simulate filtering for last month
            filtered_invoices = [inv for inv in filtered_invoices if "2024-12" in inv['date']]
            filter_applied.append(f"period: last month")
    
    # Calculate summary statistics
    total_amount = sum(inv['amount'] for inv in filtered_invoices)
    failed_count = len([inv for inv in filtered_invoices if inv['status'] == 'failed'])
    
    # Build detailed response
    filter_text = ", ".join(filter_applied) if filter_applied else "all criteria"
    
    response_text = f"📊 **Invoice Filter Results**\n\n"
    response_text += f"**Filters Applied**: {filter_text}\n"
    response_text += f"**Found**: {len(filtered_invoices)} invoices\n"
    response_text += f"**Total Amount**: ₹{total_amount:,}\n"
    if failed_count > 0:
        response_text += f"**⚠️ Failed**: {failed_count} invoices need attention\n"
    response_text += "\n**Results:**\n"
    
    for inv in filtered_invoices[:5]:  # Show top 5
        status_emoji = "❌" if inv['status'] == 'failed' else "⏳" if inv['status'] == 'pending' else "✅"
        response_text += f"{status_emoji} **{inv['invoice_id']}**: {inv['vendor']} - ₹{inv['amount']:,} ({inv['status']})"
        if inv.get('error'):
            response_text += f" - *{inv['error']}*"
        response_text += "\n"
    
    if len(filtered_invoices) > 5:
        response_text += f"\n... and {len(filtered_invoices) - 5} more invoices"
    
    # Enhanced actions list
    actions = [f"Filtered {len(filtered_invoices)} invoices by {filter_text}"]
    if failed_count > 0:
        actions.append(f"Identified {failed_count} failed invoices requiring attention")
    
    return {
        "text": response_text,
        "actions": actions,
        "data": {
            "total_found": len(filtered_invoices),
            "total_amount": total_amount,
            "failed_count": failed_count,
            "filters_applied": extracted_params
        }
    }

# Enhanced reconcile_invoices with detailed business logic
def reconcile_invoices(query, role, params=None):
    extracted_params = extract_parameters(query)
    period = extracted_params.get('period', 'current month')
    
    # Simulate realistic reconciliation data
    reconciliation_data = {
        "total_invoices": 156,
        "matched": 142,
        "mismatched": 11,
        "missing_gstr2a": 3,
        "amount_discrepancies": [
            {"invoice_id": "INV-001", "our_amount": 50000, "gstr2a_amount": 49500, "difference": 500},
            {"invoice_id": "INV-045", "our_amount": 75000, "gstr2a_amount": 73000, "difference": 2000}
        ],
        "missing_invoices": [
            {"invoice_id": "INV-078", "vendor": "TechCorp", "amount": 120000},
            {"invoice_id": "INV-091", "vendor": "DataSys", "amount": 85000}
        ]
    }
    
    match_rate = (reconciliation_data["matched"] / reconciliation_data["total_invoices"]) * 100
    
    response_text = f"🔄 **Invoice Reconciliation Complete**\n\n"
    response_text += f"**Period**: {period.title()}\n"
    response_text += f"**Match Rate**: {match_rate:.1f}%\n\n"
    
    response_text += f"📊 **Summary**:\n"
    response_text += f"• Total Processed: {reconciliation_data['total_invoices']}\n"
    response_text += f"• ✅ Matched: {reconciliation_data['matched']}\n"
    response_text += f"• ⚠️ Mismatched: {reconciliation_data['mismatched']}\n"
    response_text += f"• ❌ Missing from GSTR-2A: {reconciliation_data['missing_gstr2a']}\n\n"
    
    if reconciliation_data['amount_discrepancies']:
        response_text += f"💰 **Amount Discrepancies**:\n"
        for disc in reconciliation_data['amount_discrepancies']:
            response_text += f"• {disc['invoice_id']}: ₹{disc['difference']:,} difference\n"
        response_text += "\n"
    
    if reconciliation_data['missing_invoices']:
        response_text += f"📋 **Missing Invoices**:\n"
        for miss in reconciliation_data['missing_invoices']:
            response_text += f"• {miss['invoice_id']}: {miss['vendor']} - ₹{miss['amount']:,}\n"
    
    actions = [
        f"Reconciled {reconciliation_data['total_invoices']} invoices for {period}",
        f"Achieved {match_rate:.1f}% match rate"
    ]
    
    if reconciliation_data['mismatched'] > 0:
        actions.append(f"Flagged {reconciliation_data['mismatched']} mismatches for review")
    
    return {
        "text": response_text,
        "actions": actions,
        "data": reconciliation_data
    }

# Load action configuration
def load_action_config():
    config_path = os.path.join("config", "actions_config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def download_gst_report(query, role, params=None):
    extracted_params = extract_parameters(query)
    period = extracted_params.get('period', 'current month')
    
    # Generate report metadata
    report_data = {
        "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M')}",
        "period": period,
        "file_size": "2.3 MB",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    response_text = f"📊 **GST Report Generated**\n\n"
    response_text += f"**Report ID**: {report_data['report_id']}\n"
    response_text += f"**Period**: {period.title()}\n"
    response_text += f"**File Size**: {report_data['file_size']}\n"
    response_text += f"**Generated**: {report_data['generated_at']}\n\n"
    response_text += f"📁 File: `reports/gst_{period.replace(' ', '_')}_{report_data['report_id']}.pdf`\n"
    response_text += f"⏰ Available for download for 30 days"
    
    return {
        "text": response_text,
        "actions": [f"Generated GST report for {period}", f"Created report {report_data['report_id']}"],
        "data": report_data
    }

def view_filing_status(query, role, params=None):
    extracted_params = extract_parameters(query)
    period = extracted_params.get('period', 'current month')
    
    # Simulate filing status data
    status_data = {
        "period": period,
        "status": "Filed with delay" if "last month" in period else "Filed on time",
        "due_date": "20th of month",
        "filed_date": "22nd of month" if "last month" in period else "18th of month",
        "liability_amount": 125000,
        "itc_claimed": 45000
    }
    
    response_text = f"📝 **GST Filing Status**\n\n"
    response_text += f"**Period**: {period.title()}\n"
    response_text += f"**Status**: {status_data['status']} {'⚠️' if 'delay' in status_data['status'] else '✅'}\n"
    response_text += f"**Due Date**: {status_data['due_date']}\n"
    response_text += f"**Filed Date**: {status_data['filed_date']}\n"
    response_text += f"**Tax Liability**: ₹{status_data['liability_amount']:,}\n"
    response_text += f"**ITC Claimed**: ₹{status_data['itc_claimed']:,}"
    
    return {
        "text": response_text,
        "actions": [f"Checked filing status for {period}"],
        "data": status_data
    }

def raise_ticket(query, role, params=None):
    extracted_params = extract_parameters(query)
    priority = extracted_params.get('priority', 'medium')
    
    ticket_id = f"TCK-{datetime.now().strftime('%H%M%S')}"
    
    response_text = f"✅ **Support Ticket Created**\n\n"
    response_text += f"**Ticket ID**: {ticket_id}\n"
    response_text += f"**Priority**: {priority.title()}\n"
    response_text += f"**Issue**: {query}\n"
    response_text += f"**Assigned**: Support Team\n"
    response_text += f"**Status**: Open\n\n"
    response_text += f"🔔 You'll receive updates via email and can track progress in the tickets section."
    
    return {
        "text": response_text,
        "actions": [f"Created ticket {ticket_id} with {priority} priority"],
        "data": {"ticket_id": ticket_id, "priority": priority, "status": "open"}
    }

# Keep existing mappings but use enhanced functions
ACTION_HANDLERS = {
    "filter_invoices": filter_invoices,
    "download_gst_report": download_gst_report,
    "view_filing_status": view_filing_status,
    "reconcile_invoices": reconcile_invoices,
    "raise_ticket": raise_ticket
}

# Enhanced action patterns with more variations
ACTION_PATTERNS = {
    "filter_invoices": [
        "filter invoices", "show invoices", "find invoices", "search invoices", 
        "list invoices", "invoices for", "get invoices"
    ],
    "download_gst_report": [
        "download report", "get report", "generate report", "export report",
        "gst report", "download gst", "create report"
    ],
    "view_filing_status": [
        "filing status", "check status", "gst status", "show status",
        "filing for", "check filing", "status of filing"
    ],
    "reconcile_invoices": [
        "reconcile", "match invoices", "compare invoices", "reconcile invoices",
        "invoice reconciliation", "match with gstr"
    ],
    "raise_ticket": [
        "raise ticket", "create ticket", "new ticket", "open ticket",
        "support ticket", "help ticket", "ticket for"
    ]
}

def handle_action(query: str, role: str):
    """Enhanced action handler with better parameter extraction and business logic"""
    query_lower = query.lower()
    
    # Check permissions
    action_config = load_action_config()
    allowed_actions = [a["name"] for a in action_config if role.lower() in [r.lower() for r in a["role_access"]]]
    
    # Enhanced pattern matching
    for action_name, patterns in ACTION_PATTERNS.items():
        if action_name not in allowed_actions:
            continue
            
        # Check if any pattern matches
        if any(pattern in query_lower for pattern in patterns):
            handler = ACTION_HANDLERS.get(action_name)
            if handler:
                try:
                    result = handler(query, role)
                    # Add execution metadata
                    result["execution_time"] = datetime.now().strftime("%H:%M:%S")
                    result["executed_by"] = role
                    return result
                except Exception as e:
                    return {
                        "text": f"⚠️ Error executing {action_name}: {str(e)}",
                        "actions": [f"Error in {action_name}"],
                        "error": True
                    }
    
    return None