from typing import Dict, Any
from inflect_gtm.components.utils.meeting_log_parser import parse_meeting_log
from inflect_gtm.tools.google_calendar.google_calendar_tool import GoogleCalendarTool
from inflect_gtm.components.rag.retriever import query_similar_documents
from inflect_gtm.components.utils.rag_prompt_builder import build_followup_prompt
from inflect_gtm.components.utils.llm import call_llm


def run_rag_pipeline(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the full RAG pipeline to generate a personalized follow-up email.

    Steps:
    1. Parse the raw meeting log
    2. Resolve Google Calendar event and enrich parsed data
    3. Retrieve similar documents from vector DB
    4. Construct a prompt using all retrieved context
    5. Generate follow-up email via LLM

    Args:
        context (Dict[str, Any]): Input data with meeting log and user metadata

    Returns:
        Dict[str, Any]: All intermediate and final outputs including prompt and LLM result
    """
    # Step 1: Parse meeting log
    meeting_log_raw = context.get("meeting_log", "")
    parsed_log = parse_meeting_log(meeting_log_raw)

    # Step 2: Resolve event from calendar (find or create)
    calendar_tool = GoogleCalendarTool()
    resolved_event = calendar_tool.resolve_event(parsed_log)

    # Enrich parsed log using calendar data
    enriched_log = {
        "subject": parsed_log.get("subject", ""),
        "summary": parsed_log.get("summary", ""),
        "action_items": parsed_log.get("action_items", []),
        "participants": [],  # names
        "emails": [],        # emails
        "start_time": None,
        "end_time": None,
        "source": resolved_event.get("source", "log-only")
    }

    if resolved_event:
        enriched_log["start_time"] = resolved_event.get("start_time")
        enriched_log["end_time"] = resolved_event.get("end_time")

        # Trust calendar names and emails when available
        calendar_participants = resolved_event.get("participants", [])
        enriched_log["participants"] = [p.get("displayName", "") for p in calendar_participants if p.get("displayName")]
        enriched_log["emails"] = [p.get("email", "") for p in calendar_participants if p.get("email")]

        # If subject from log is weak, trust calendar only if log subject is missing
        if not enriched_log["subject"]:
            enriched_log["subject"] = resolved_event.get("subject", "")

    # Step 3: Document retrieval using meeting summary
    retrieved_docs = query_similar_documents(enriched_log.get("summary", ""), top_k=3)

    # Step 4: Prompt generation
    prompt_context = {
        "meeting_log": enriched_log,
        "user_name": context.get("user_name", "[Your Name]"),
        "retrieved_docs": retrieved_docs,
    }
    prompt = build_followup_prompt(prompt_context)

    # Step 5: LLM generation
    llm_output = call_llm(prompt)

    return {
        "prompt": prompt,
        "llm_output": llm_output,
        "enriched_meeting_log": enriched_log,
        "retrieved_docs": retrieved_docs
    }


# Pipeline test
if __name__ == "__main__":
    test_context = {
        "meeting_log": """
Met with Sarah and James to discuss the new onboarding flow. 
Sarah asked for a demo of the integrations and seemed excited about the Slack integration.
James requested a follow-up on pricing tiers. 
Next steps: send them the latest slide deck and book a call with technical support.
""",
        "user_name": "Mintae Kim"
    }

    result = run_rag_pipeline(test_context)

    print("\n📨 Prompt Used:\n")
    print(result["prompt"])
    print("\n📬 LLM Output:\n")
    print(result["llm_output"])