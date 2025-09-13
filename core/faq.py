import json
import os

def match_faq(query):
    path = os.path.join("data", "faqs.json")
    with open(path, "r") as f:
        faqs = json.load(f)
    for faq in faqs:
        if faq["question"].lower() in query:
            return faq["answer"]
    return None
