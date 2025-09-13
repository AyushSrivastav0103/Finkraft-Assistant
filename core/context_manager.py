import json
import os
from datetime import datetime

# Path to store conversation history
CONVERSATION_HISTORY_PATH = os.path.join("data", "conversation_history.json")

# Initialize conversation history file if it doesn't exist
def initialize_history_file():
    if not os.path.exists(CONVERSATION_HISTORY_PATH):
        with open(CONVERSATION_HISTORY_PATH, "w") as f:
            json.dump({}, f)

# Save conversation to history
def save_conversation(user_id, query, response, context=None):
    initialize_history_file()
    
    with open(CONVERSATION_HISTORY_PATH, "r") as f:
        history = json.load(f)
    
    # Initialize user history if not exists
    if user_id not in history:
        history[user_id] = []
    
    # Add new conversation entry
    history[user_id].append({
        "timestamp": str(datetime.now()),
        "query": query,
        "response": response,
        "context": context or {}
    })
    
    # Limit history size (keep last 20 conversations)
    if len(history[user_id]) > 20:
        history[user_id] = history[user_id][-20:]
    
    with open(CONVERSATION_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

# Get conversation history for a user
def get_conversation_history(user_id, limit=5):
    initialize_history_file()
    
    with open(CONVERSATION_HISTORY_PATH, "r") as f:
        history = json.load(f)
    
    if user_id in history:
        return history[user_id][-limit:]
    return []

# Get relevant context from previous conversations
def get_relevant_context(user_id, query):
    history = get_conversation_history(user_id)
    # Simple implementation - return recent history
    # In a real system, this would use semantic search or embeddings
    return history

# Fetch relevant email based on query
def fetch_relevant_email(query):
    # Load sample emails
    email_path = os.path.join("data", "sample_emails.json")
    with open(email_path, "r") as f:
        emails = json.load(f)
    
    # Simple keyword matching (in a real system, use embeddings or NLP)
    query_terms = query.lower().split()
    best_match = None
    highest_score = 0
    
    for email in emails:
        score = 0
        email_text = (email["subject"] + " " + email["body"]).lower()
        
        for term in query_terms:
            if term in email_text:
                score += 1
        
        if score > highest_score:
            highest_score = score
            best_match = email
    
    if best_match and highest_score > 1:  # At least 2 matching terms
        return f"📧 **{best_match['subject']}**\n\n{best_match['body']}\n\nSent on: {best_match['date']}"
    
    return None