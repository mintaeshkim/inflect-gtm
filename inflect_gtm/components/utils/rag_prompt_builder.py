from typing import Dict, Any, List


def build_followup_prompt(context: Dict[str, Any]) -> str:
    """
    Builds a prompt string for generating a professional follow-up email,
    using structured RAG context including meeting logs, calendar events,
    retrieved document snippets, etc.
    """
    log = context.get("meeting_log", {})
    events: List[Dict[str, str]] = context.get("calendar_events", [])
    retrieved_docs: List[str] = context.get("retrieved_docs", [])
    user_name = context.get("user_name", "[Your Name]")

    participants = ", ".join(log.get("participants", [])) or "the client"
    summary = log.get("summary", "No summary provided.")
    action_items = log.get("action_items", [])

    actions_text = ""
    if action_items:
        actions_text = "\n\nAction items discussed:\n" + "\n".join(f"- {item}" for item in action_items)

    event_text = ""
    if events:
        event_text += "\n\nUpcoming related calendar events:\n"
        for e in events:
            event_text += f"- {e['summary']} ({e['start']} to {e['end']})\n"

    doc_text = ""
    if retrieved_docs:
        doc_text = "\n\nRelevant documents retrieved:\n"
        for i, doc in enumerate(retrieved_docs[:5]):  # truncate to 5 docs max
            doc_text += f"{i+1}. {doc.strip()}\n"

    prompt = f"""You are an AI assistant helping to write a professional follow-up email.

Meeting Participants: {participants}
Meeting Summary: {summary}{actions_text}{event_text}{doc_text}

Write a professional email that:
- Recaps the meeting
- Thanks the participants
- Includes action items or attachments
- Proposes next steps if appropriate

Use a friendly but professional tone. Address the participants directly.

End the email with:
Best regards,  
{user_name}
"""

    return prompt


if __name__ == "__main__":
    print("🧪 Testing RAG prompt builder with retrieved_docs...")
    example_context = {
        "meeting_log": {
            "participants": ["Sarah", "James"],
            "summary": "Discussed onboarding and integration features.",
            "action_items": ["Send latest slide deck", "Schedule technical support call"]
        },
        "calendar_events": [
            {
                "summary": "Tech support call",
                "start": "2024-06-01T10:00:00Z",
                "end": "2024-06-01T10:30:00Z"
            }
        ],
        "retrieved_docs": [
            "The onboarding checklist includes Slack and Salesforce integrations.",
            "Pricing tiers are being updated to reflect the new usage model.",
            "Customers in the sales department often prefer Slack integration over email-based workflows."
        ],
        "user_name": "Mintae Kim"
    }

    prompt = build_followup_prompt(example_context)
    print("\n📝 Generated Prompt:\n")
    print(prompt)