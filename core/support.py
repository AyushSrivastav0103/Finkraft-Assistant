import json
import os
from datetime import datetime

TICKET_PATH = os.path.join("data", "tickets.json")

def create_ticket(summary):
    with open(TICKET_PATH, "r") as f:
        tickets = json.load(f)

    new_id = f"TCK-{len(tickets)+101}"
    new_ticket = {
        "ticket_id": new_id,
        "summary": summary,
        "status": "open",
        "priority": "medium",
        "created_at": str(datetime.now().date()),
        "updated_at": str(datetime.now().date()),
        "assigned_to": "Support Team"
    }

    tickets.append(new_ticket)
    with open(TICKET_PATH, "w") as f:
        json.dump(tickets, f, indent=2)

    return new_id

def track_ticket(query):
    with open(TICKET_PATH, "r") as f:
        tickets = json.load(f)
    for t in tickets:
        if t["ticket_id"].lower() in query:
            return f"🎫 Ticket {t['ticket_id']} is {t['status']} (Priority: {t['priority']})."
    return "No matching ticket found."
