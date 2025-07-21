import json
from typing import Dict, Any
from inflect_gtm.components.utils.llm import call_llm


def parse_meeting_log(log: str) -> Dict[str, Any]:
    """
    Parses a natural language meeting log and extracts structured fields.

    Returns:
    {
        "participants": ["sarah@example.com", "james@example.com"],
        "summary": "Slack integration discussion",
        "subject": "Slack integration discussion",
        "action_items": ["Send latest slide deck", "Book call with technical support"],
        "start_time": "optional placeholder, to be filled via calendar resolution",
        "end_time": "optional placeholder, to be filled via calendar resolution"
    }
    """
    prompt = f"""
You are a helpful assistant that extracts structured information from meeting notes.

Given the following meeting log, extract and return a JSON object with the following fields:

1. "participants": list of names mentioned in the meeting (first name only is fine)
2. "summary": 1-2 sentence abstract of the meeting
3. "subject": short phrase for the meeting subject (e.g., "Slack integration discussion")
4. "action_items": list of action items discussed
5. "start_time": null (leave as null for now)
6. "end_time": null (leave as null for now)

ONLY return a valid JSON object. No markdown, no explanation, no prefix.

Meeting Log:
\"\"\"{log}\"\"\"
"""

    response = call_llm(prompt)

    try:
        # Remove any code block markers
        match = response.strip()
        if match.startswith("```json"):
            match = match.removeprefix("```json").removesuffix("```").strip()
        elif match.startswith("```"):
            match = match.removeprefix("```").removesuffix("```").strip()

        return json.loads(match)
    except Exception as e:
        return {
            "error": f"Failed to parse JSON from LLM output: {e}",
            "raw_response": response
        }


if __name__ == "__main__":
    print("🚀 Testing LLM-based meeting log parser...\n")
    example_log = """
Met with Sarah and James to discuss the new onboarding flow. 
Sarah asked for a demo of the integrations and seemed excited about the Slack integration.
James requested a follow-up on pricing tiers. 
Next steps: send them the latest slide deck and book a call with technical support.
"""

    result = parse_meeting_log(example_log)

    print("✅ Parsed Result:\n")
    print(json.dumps(result, indent=2))