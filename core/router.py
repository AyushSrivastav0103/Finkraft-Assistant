import re
import random
from core import faq, support, actions, context_manager as cm
from utils import trace_logger

# Router returns (response, trace_info)
def route_query(query: str, role: str, faqs, emails, tickets, action_config, user_id=None):
    query_lower = query.lower()

    # 1. FAQ handling
    faq_answer = faq.match_faq(query_lower)
    if faq_answer:
        trace_logger.log_trace(query, faq_answer, "FAQ Module")
        return {"text": faq_answer}, "FAQ Module"

    # 2. Email/system queries
    if any(word in query_lower for word in ["email", "notification", "alert", "status update"]):
        email_response = cm.fetch_relevant_email(query_lower)
        if email_response:
            trace_logger.log_trace(query, email_response, "Email Module")
            return {"text": email_response}, "Email Module"

    # 3. Support tickets
    if "ticket" in query_lower or "support" in query_lower:
        if "create" in query_lower or "raise" in query_lower:
            ticket_id = support.create_ticket(summary=query)
            trace_logger.log_trace(query, f"✅ Ticket {ticket_id} created for: {query}", "Support Module (Create Ticket)")
            return {
                "text": f"✅ Ticket {ticket_id} created for: {query}",
                "actions": [f"Created ticket {ticket_id}"]
            }, "Support Module (Create Ticket)"

        elif "status" in query_lower or "track" in query_lower:
            ticket_status = support.track_ticket(query_lower)
            trace_logger.log_trace(query, ticket_status, "Support Module (Track Ticket)")
            return {
                "text": ticket_status,
                "actions": ["Checked ticket status"]
            }, "Support Module (Track Ticket)"

    # 4. Actions (from config-driven actions.py)
    action_result = actions.handle_action(query_lower, role)
    if action_result:
        trace_logger.log_trace(query, str(action_result), "Actions Module")
        return action_result, "Actions Module"

    # 5. Check context for relevant information
    if user_id:
        context_history = cm.get_relevant_context(user_id, query_lower)
        if context_history:
            # Use context to enhance response (simple implementation)
            context_msg = "I see we've discussed this before. Based on our previous conversation: "
            # Get the most relevant previous response
            for conv in reversed(context_history):
                if any(term in conv["query"].lower() for term in query_lower.split()):
                    context_msg += f"\n\nPreviously you asked: '{conv['query']}'\nAnd I responded: '{conv['response'][:100]}...'"
                    trace_logger.log_trace(query, context_msg, "Context-Enhanced Response")
                    return {"text": context_msg}, "Context-Enhanced Response"
    
    # 6. Fallback
    fallback_msg = random.choice([
        "🤔 I didn't quite get that. Could you rephrase?",
        "I'm not sure what you mean. Try asking about invoices, filings, or tickets.",
        "Sorry, I didn't understand. Do you want me to filter invoices, raise a ticket, or explain something?"
    ])
    trace_logger.log_trace(query, fallback_msg, "Fallback")
    return {"text": fallback_msg}, "Fallback"
