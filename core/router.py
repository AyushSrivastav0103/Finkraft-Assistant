import re
import random
from core import faq, support, actions, context_manager as cm
from utils import trace_logger

def analyze_query_complexity(query: str) -> dict:
    """Analyze query to determine complexity and routing strategy"""
    analysis = {
        'word_count': len(query.split()),
        'has_parameters': bool(re.search(r'[=]|\b(vendor|status|period|last|this)\b', query, re.IGNORECASE)),
        'has_entities': bool(re.search(r'\b(INV-\d+|TCK-\d+|₹[\d,]+)\b', query, re.IGNORECASE)),
        'question_words': len(re.findall(r'\b(what|why|how|when|where|who)\b', query, re.IGNORECASE)),
        'action_words': len(re.findall(r'\b(filter|download|create|show|generate|reconcile)\b', query, re.IGNORECASE))
    }

    # Determine complexity
    if analysis['word_count'] > 10 or analysis['has_parameters'] or analysis['has_entities']:
        analysis['complexity'] = 'high'
    elif analysis['question_words'] > 0 or analysis['action_words'] > 0:
        analysis['complexity'] = 'medium'
    else:
        analysis['complexity'] = 'low'

    return analysis

def enhance_response_with_context(response: dict, context_data: dict, query: str) -> dict:
    """Enhance response with relevant contextual information"""
    if not isinstance(response, dict) or not context_data:
        return response

    suggestions = []

    open_tickets = context_data.get('open_tickets', [])
    if open_tickets and 'ticket' not in query.lower():
        suggestions.append(f"You have {len(open_tickets)} open tickets - would you like to check their status?")

    if context_data.get('average_satisfaction', 1.0) < 0.7:
        suggestions.append("I notice some previous queries might need follow-up - let me know if you need help with anything.")

    recent_topics = context_data.get('recent_topics', [])
    if recent_topics and any(
        word in query.lower() for topic in recent_topics for word in topic.lower().split()
    ):
        suggestions.append("This seems related to our recent discussion - I can provide more details if needed.")

    if suggestions:
        response['context_suggestions'] = suggestions[:2]

    return response

def route_query(query: str, role: str, faqs, emails, tickets, action_config, user_id=None):
    """Enhanced router with smart context integration and better decision making"""
    query_lower = query.lower()

    query_analysis = analyze_query_complexity(query)

    context_data = {}
    if user_id:
        try:
            context_data = cm.get_context_summary(user_id)
            relevant_context = cm.get_relevant_context(user_id, query)
        except Exception:
            relevant_context = []
    else:
        relevant_context = []

    response = None
    trace_info = ""
    confidence_score = 0.5

    try:
        # 1. FAQ handling
        if query_analysis['question_words'] > 0 or any(word in query_lower for word in ["why", "how", "what", "explain"]):
            faq_answer = faq.match_faq(query_lower)
            if faq_answer:
                response = {"text": faq_answer}
                trace_info = "FAQ Module"
                confidence_score = 0.9

                if relevant_context:
                    context_addition = "\n\n💡 **Based on our previous discussions**: "
                    for ctx in relevant_context[:1]:
                        if ctx.get('intent') == 'explanation':
                            context_addition += f"You previously asked about '{ctx['query'][:50]}...'"
                            break
                    response["text"] += context_addition
                    confidence_score = 0.95

        # 2. Email/notification queries
        if not response and any(
            phrase in query_lower
            for phrase in ["email", "notification", "alert", "status update", "reminder"]
        ):
            email_response = cm.fetch_relevant_email(query_lower)
            if email_response:
                response = {"text": email_response}
                trace_info = "Enhanced Email Module"
                confidence_score = 0.85  # bumped slightly

        # 3. Support tickets
        if not response and ("ticket" in query_lower or "support" in query_lower):
            if "create" in query_lower or "raise" in query_lower:
                priority = "medium"
                if context_data.get('average_satisfaction', 1.0) < 0.5:
                    priority = "high"

                ticket_id = support.create_ticket(summary=query)
                response_text = f"✅ Ticket {ticket_id} created with {priority} priority for: {query}"

                if context_data.get('open_tickets'):
                    open_count = len(context_data['open_tickets'])
                    response_text += f"\n\n📋 Note: You currently have {open_count} other open tickets."

                response = {
                    "text": response_text,
                    "actions": [f"Created ticket {ticket_id}", f"Set priority to {priority}"]
                }
                trace_info = "Enhanced Support Module (Create)"
                confidence_score = 0.95

            elif "status" in query_lower or "track" in query_lower:
                ticket_status = support.track_ticket(query_lower)

                if context_data.get('open_tickets'):
                    ticket_status += f"\n\nYour other open tickets:"
                    for ticket in context_data['open_tickets'][:3]:
                        ticket_status += f"\n• {ticket['ticket_id']}: {ticket['summary'][:40]}... ({ticket['status']})"

                response = {
                    "text": ticket_status,
                    "actions": ["Checked ticket status", "Provided ticket overview"]
                }
                trace_info = "Enhanced Support Module (Track)"
                confidence_score = 0.85

        # 4. Actions
        if not response:
            action_result = actions.handle_action(query_lower, role)
            if action_result:
                response = action_result
                trace_info = "Enhanced Actions Module"
                confidence_score = 0.9

                if context_data.get('most_common_intent') == 'data_retrieval' and response.get('data'):
                    response.setdefault('next_steps', []).append("Export this data to Excel")

        # 5. Context follow-up
        if not response and user_id and relevant_context:
            best_context = relevant_context[0]
            followup_indicators = ["why", "how", "more details", "explain", "what about", "also"]
            if any(indicator in query_lower for indicator in followup_indicators):
                context_msg = f"Based on our previous discussion about '{best_context['query'][:50]}...':\n\n"
                context_msg += f"**Previous context**: {best_context['response'][:150]}...\n\n"
                context_msg += "**For your current question**: Let me provide more specific information."

                if best_context.get('intent') == 'data_retrieval':
                    context_msg += " Would you like me to show you the detailed data or run a new filter?"
                elif best_context.get('intent') == 'explanation':
                    context_msg += " I can provide more technical details or specific examples if needed."

                response = {"text": context_msg}
                trace_info = "Enhanced Context Module"
                confidence_score = 0.75

        # 6. Fallback
        if not response:
            common_intent = context_data.get('most_common_intent', 'general')
            fallback_suggestions = {
                'data_retrieval': [
                    "Try: 'Filter invoices from last month'",
                    "Try: 'Show pending invoices'",
                    "Try: 'List reconciled invoices'"
                ],
                'report_generation': [
                    "Try: 'Download GST report for Q1'",
                    "Try: 'Generate monthly report'",
                    "Try: 'Export reconciliation summary'"
                ],
                'explanation': [
                    "Try: 'Why did my GST filing fail?'",
                    "Try: 'Explain invoice mismatch'",
                    "Try: 'What is reconciliation?'"
                ],
                'creation': [
                    "Try: 'Create ticket for invoice issue'",
                    "Try: 'Raise urgent ticket'",
                    "Try: 'Open support request'"
                ]
            }

            suggestions = fallback_suggestions.get(common_intent, [
                "Try asking about invoices, GST reports, or support tickets",
                "Use specific keywords like 'filter', 'download', or 'create'",
                "Check the help documentation for available commands"
            ])

            fallback_msg = f"🤔 I'm not sure what you're looking for. Based on your usual queries, here are some suggestions:\n\n"
            fallback_msg += "\n".join([f"• {s}" for s in suggestions[:3]])

            if context_data.get('total_conversations', 0) > 0:
                fallback_msg += f"\n\n💡 I see we've had {context_data['total_conversations']} conversations. Feel free to ask follow-up questions about previous topics!"

            response = {
                "text": fallback_msg,
                "suggestions": suggestions[:3],
                "context_aware": True
            }
            trace_info = "Intelligent Fallback"
            confidence_score = 0.5  # lifted slightly

        # Add context + trace
        if response and context_data:
            response = enhance_response_with_context(response, context_data, query)
            response["confidence_score"] = confidence_score
            response["query_analysis"] = query_analysis

        trace_data = {
            "confidence": confidence_score,
            "complexity": query_analysis['complexity'],
            "context_used": bool(relevant_context),
            "user_context_summary": {
                "total_conversations": context_data.get('total_conversations', 0),
                "common_intent": context_data.get('most_common_intent', 'unknown')
            } if context_data else {}
        }

        trace_logger.log_trace(query, response, trace_info, trace_data)
        return response, trace_info

    except Exception as e:
        error_response = {
            "text": f"⚠️ I encountered an error: {str(e)}",
            "error": True,
            "confidence_score": 0.1
        }
        trace_logger.log_trace(query, error_response, "Error Handler")
        return error_response, "Error Handler"

def explain_failure_reasons(query: str, failed_items: list) -> str:
    """Explain why specific items failed with business context"""
    explanations = []

    for item in failed_items:
        err = (item.get('error') or '').lower()
        if "gstin" in err:
            explanations.append(f"• **{item['invoice_id']}**: Missing GSTIN - Supplier hasn't provided valid GSTIN number")
        elif "hsn" in err:
            explanations.append(f"• **{item['invoice_id']}**: Invalid HSN code - Product classification code is incorrect")
        elif "amount" in err:
            explanations.append(f"• **{item['invoice_id']}**: Amount mismatch - Invoice amount doesn't match supplier's filing")
        else:
            explanations.append(f"• **{item['invoice_id']}**: {item.get('error', 'Unknown error')}")

    return "\n".join(explanations)