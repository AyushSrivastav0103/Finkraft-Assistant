import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Path to store conversation history
CONVERSATION_HISTORY_PATH = os.path.join("data", "conversation_history.json")

def initialize_history_file():
    if not os.path.exists(CONVERSATION_HISTORY_PATH):
        with open(CONVERSATION_HISTORY_PATH, "w") as f:
            json.dump({}, f)

def save_conversation(user_id, query, response, context=None):
    initialize_history_file()
    
    with open(CONVERSATION_HISTORY_PATH, "r") as f:
        history = json.load(f)
    
    if user_id not in history:
        history[user_id] = []
    
    # Enhanced conversation entry with metadata
    conversation_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response": response,
        "context": context or {},
        "entities": extract_entities(query),  # Extract business entities
        "intent": classify_intent(query),     # Classify the intent
        "satisfaction_score": calculate_satisfaction(response)  # Estimate satisfaction
    }
    
    history[user_id].append(conversation_entry)
    
    # Keep last 30 conversations (increased from 20)
    if len(history[user_id]) > 30:
        history[user_id] = history[user_id][-30:]
    
    with open(CONVERSATION_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract business entities from text"""
    import re
    
    entities = {}
    
    # Invoice IDs
    invoice_ids = re.findall(r'\bINV[-_]\d+\b', text, re.IGNORECASE)
    if invoice_ids:
        entities['invoice_ids'] = invoice_ids
    
    # Ticket IDs  
    ticket_ids = re.findall(r'\bTCK[-_]\d+\b', text, re.IGNORECASE)
    if ticket_ids:
        entities['ticket_ids'] = ticket_ids
    
    # Amounts
    amounts = re.findall(r'₹[\d,]+|\d+\s*rupees?', text, re.IGNORECASE)
    if amounts:
        entities['amounts'] = amounts
    
    # Dates/Periods
    periods = re.findall(r'\b(?:last|this|next)\s+(?:month|quarter|year)\b|Q[1-4]\s*20\d{2}', text, re.IGNORECASE)
    if periods:
        entities['periods'] = periods
    
    # Vendors (simple detection)
    vendor_patterns = [r'vendor\s+([A-Za-z\s]+)', r'from\s+([A-Za-z\s]+?)(?:\s|,|$)']
    for pattern in vendor_patterns:
        vendors = re.findall(pattern, text, re.IGNORECASE)
        if vendors:
            entities['vendors'] = [v.strip() for v in vendors]
            break
    
    return entities

def classify_intent(query: str) -> str:
    """Classify the intent of the query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['filter', 'show', 'list', 'find']):
        return 'data_retrieval'
    elif any(word in query_lower for word in ['download', 'export', 'generate']):
        return 'report_generation'
    elif any(word in query_lower for word in ['create', 'raise', 'new']):
        return 'creation'
    elif any(word in query_lower for word in ['why', 'how', 'what', 'explain']):
        return 'explanation'
    elif any(word in query_lower for word in ['status', 'check', 'track']):
        return 'status_inquiry'
    else:
        return 'general'

def calculate_satisfaction(response: str) -> float:
    """Estimate user satisfaction based on response characteristics"""
    if isinstance(response, dict):
        response_text = response.get('text', '')
        has_actions = bool(response.get('actions', []))
    else:
        response_text = str(response)
        has_actions = False
    
    score = 0.5  # Base score
    
    # Positive indicators
    if len(response_text) > 100:  # Detailed response
        score += 0.2
    if has_actions:  # Actually performed actions
        score += 0.2
    if any(word in response_text.lower() for word in ['✅', '📊', '📄', '🔄']):  # Contains emojis/formatting
        score += 0.1
    
    # Negative indicators
    if any(word in response_text.lower() for word in ['error', 'failed', 'sorry']):
        score -= 0.3
    if len(response_text) < 30:  # Very short response
        score -= 0.2
    
    return max(0.0, min(1.0, score))  # Clamp between 0 and 1

def get_conversation_history(user_id, limit=5):
    initialize_history_file()
    
    with open(CONVERSATION_HISTORY_PATH, "r") as f:
        history = json.load(f)
    
    if user_id in history:
        return history[user_id][-limit:]
    return []

def get_relevant_context(user_id: str, query: str) -> List[Dict[str, Any]]:
    """Enhanced context retrieval with semantic matching"""
    history = get_conversation_history(user_id, 15)  # Get more history
    
    if not history:
        return []
    
    # Extract entities from current query
    current_entities = extract_entities(query)
    current_intent = classify_intent(query)
    query_words = set(query.lower().split())
    
    # Score conversations for relevance
    scored_conversations = []
    
    for conv in history:
        score = 0.0
        
        # Intent matching (highest priority)
        if conv.get('intent') == current_intent:
            score += 0.4
        
        # Entity matching
        conv_entities = conv.get('entities', {})
        for entity_type in current_entities:
            if entity_type in conv_entities:
                # Check for actual entity overlap
                current_values = set(str(v).lower() for v in current_entities[entity_type])
                conv_values = set(str(v).lower() for v in conv_entities[entity_type])
                if current_values.intersection(conv_values):
                    score += 0.3
        
        # Keyword matching
        conv_words = set(conv['query'].lower().split())
        word_overlap = len(query_words.intersection(conv_words))
        if word_overlap > 0:
            score += (word_overlap / len(query_words)) * 0.2
        
        # Recency bonus (more recent = higher score)
        try:
            conv_time = datetime.fromisoformat(conv['timestamp'])
        except ValueError:
            # fallback for old entries saved as str(datetime.now())
            try:
                conv_time = datetime.strptime(conv['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
            except:
                conv_time = None

        if conv_time:
            hours_ago = (datetime.now() - conv_time).total_seconds() / 3600
            if hours_ago < 24:  # Within last day
                score += 0.1 * (1 - hours_ago / 24)
        
        if score > 0.2:  # Only include reasonably relevant conversations
            scored_conversations.append((score, conv))
    
    # Sort by score and return top matches
    scored_conversations.sort(key=lambda x: x[0], reverse=True)
    
    return [conv for score, conv in scored_conversations[:3]]

def get_context_summary(user_id: str) -> Dict[str, Any]:
    """Get a comprehensive context summary for the user"""
    history = get_conversation_history(user_id, 20)
    
    if not history:
        return {"summary": "No conversation history available"}
    
    # Analyze conversation patterns
    intents = [conv.get('intent', 'general') for conv in history]
    entities = {}
    total_satisfaction = 0
    
    for conv in history:
        # Aggregate entities
        conv_entities = conv.get('entities', {})
        for entity_type, entity_list in conv_entities.items():
            if entity_type not in entities:
                entities[entity_type] = set()
            entities[entity_type].update(entity_list)
        
        # Average satisfaction
        total_satisfaction += conv.get('satisfaction_score', 0.5)
    
    # Convert sets back to lists for JSON serialization
    entities = {k: list(v) for k, v in entities.items()}
    
    # Most common intent
    from collections import Counter
    intent_counts = Counter(intents)
    most_common_intent = intent_counts.most_common(1)[0][0] if intent_counts else 'general'
    
    avg_satisfaction = total_satisfaction / len(history) if history else 0.5
    
    return {
        "total_conversations": len(history),
        "most_common_intent": most_common_intent,
        "entities_mentioned": entities,
        "average_satisfaction": round(avg_satisfaction, 2),
        "recent_topics": [conv['query'][:50] + "..." if len(conv['query']) > 50 else conv['query'] 
                         for conv in history[-3:]],
        "intent_distribution": dict(intent_counts)
    }

def search_conversation_history(user_id: str, search_term: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search through conversation history"""
    history = get_conversation_history(user_id, 50)  # Search through more history
    
    search_lower = search_term.lower()
    matches = []
    
    for conv in history:
        relevance_score = 0
        
        # Check query content
        if search_lower in conv['query'].lower():
            relevance_score += 2
        
        # Check response content
        response_text = conv['response'] if isinstance(conv['response'], str) else str(conv['response'])
        if search_lower in response_text.lower():
            relevance_score += 1
        
        # Check entities
        entities = conv.get('entities', {})
        for entity_list in entities.values():
            if any(search_lower in str(entity).lower() for entity in entity_list):
                relevance_score += 1.5
        
        if relevance_score > 0:
            matches.append({
                'conversation': conv,
                'relevance': relevance_score
            })
    
    # Sort by relevance and return top matches
    matches.sort(key=lambda x: x['relevance'], reverse=True)
    return [match['conversation'] for match in matches[:limit]]

def get_open_items_context(user_id: str) -> Dict[str, Any]:
    """Get context about open tickets and pending items"""
    # Load tickets
    try:
        with open(os.path.join("data", "tickets.json"), "r") as f:
            all_tickets = json.load(f)
    except:
        all_tickets = []
    
    # Find tickets created by this user (simplified - in real system would track user association)
    recent_history = get_conversation_history(user_id, 10)
    user_tickets = []
    
    for conv in recent_history:
        if conv.get('intent') == 'creation' and 'ticket' in conv['query'].lower():
            # Extract ticket ID from response if available
            response_text = str(conv['response'])
            import re
            ticket_match = re.search(r'TCK-\d+', response_text)
            if ticket_match:
                ticket_id = ticket_match.group(0)
                # Find this ticket in the tickets list
                for ticket in all_tickets:
                    if ticket['ticket_id'] == ticket_id:
                        user_tickets.append(ticket)
                        break
    
    # Get pending actions from recent conversations
    pending_actions = []
    for conv in recent_history[-5:]:  # Last 5 conversations
        if conv.get('intent') in ['data_retrieval', 'report_generation']:
            if conv.get('satisfaction_score', 0.5) < 0.7:  # Low satisfaction might indicate incomplete task
                pending_actions.append({
                    'query': conv['query'],
                    'timestamp': conv['timestamp'],
                    'status': 'needs_followup'
                })
    
    return {
        'open_tickets': [t for t in user_tickets if t.get('status') != 'closed'],
        'pending_actions': pending_actions,
        'total_interactions': len(recent_history)
    }

# Enhanced fetch_relevant_email function
def fetch_relevant_email(query):
    """Enhanced email fetching with entity matching"""
    email_path = os.path.join("data", "sample_emails.json")
    try:
        with open(email_path, "r") as f:
            emails = json.load(f)
    except:
        return None
    
    # Extract entities from query
    query_entities = extract_entities(query)
    query_terms = query.lower().split()
    
    best_match = None
    highest_score = 0
    
    for email in emails:
        score = 0
        email_text = (email["subject"] + " " + email["body"]).lower()
        
        # Basic keyword matching
        for term in query_terms:
            if term in email_text:
                score += 1
        
        # Entity-based matching (higher priority)
        for entity_type, entity_values in query_entities.items():
            for value in entity_values:
                if str(value).lower() in email_text:
                    score += 3  # Higher weight for entity matches
        
        # Category matching
        email_category = email.get("category", "").lower()
        if any(term in email_category for term in query_terms):
            score += 2
        
        # Intent-based matching
        query_intent = classify_intent(query)
        if query_intent == 'explanation' and any(word in email_text for word in ['failed', 'error', 'issue']):
            score += 2
        elif query_intent == 'status_inquiry' and any(word in email_text for word in ['status', 'update', 'completed']):
            score += 2
        
        if score > highest_score:
            highest_score = score
            best_match = email
    
    if best_match and highest_score > 1:
        return f"📧 **{best_match['subject']}**\n\n{best_match['body']}\n\n**Category**: {best_match.get('category', 'General')}\n**Date**: {best_match['date']}"
    
    return None