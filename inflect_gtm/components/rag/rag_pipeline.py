from typing import Dict, Any, List
from inflect_gtm.components.utils.meeting_log_parser import parse_meeting_log
from inflect_gtm.tools.google_calendar.google_calendar_tool import GoogleCalendarTool
from inflect_gtm.components.rag.retriever import query_similar_documents
from inflect_gtm.components.utils.rag_prompt_builder import build_followup_prompt
from inflect_gtm.components.utils.llm import call_llm


def run_rag_pipeline(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs the complete RAG pipeline for generating a follow-up email.
    Steps:
    1. Parse meeting log
    2. Fetch upcoming calendar events
    3. Retrieve similar documents
    4. Build prompt
    5. Call LLM to generate follow-up email
    """
    # Step 1: Parse meeting log
    meeting_log_raw = context.get("meeting_log", "")
    parsed_log = parse_meeting_log(meeting_log_raw)

    # Step 2: Fetch calendar events
    calendar_tool = GoogleCalendarTool()
    calendar_data = calendar_tool.get_upcoming_events({"n": 3})
    calendar_events = calendar_data.get("events", [])

    # Step 3: Retrieve relevant documents using parsed summary
    retrieved_docs = query_similar_documents(parsed_log.get("summary", ""), k=3)

    # Step 4: Build follow-up email prompt
    prompt_context = {
        "meeting_log": parsed_log,
        "calendar_events": calendar_events,
        "retrieved_docs": retrieved_docs,
        "user_name": context.get("user_name", "[Your Name]")
    }
    prompt = build_followup_prompt(prompt_context)

    # Step 5: Generate email using LLM
    llm_output = call_llm(prompt)

    return {
        "prompt": prompt,
        "llm_output": llm_output,
        "parsed_meeting_log": parsed_log,
        "calendar_events": calendar_events,
        "retrieved_docs": retrieved_docs
    }


# Example usage
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