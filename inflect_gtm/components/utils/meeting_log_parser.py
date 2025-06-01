import json
from typing import Dict, Any
from inflect_gtm.components.utils.llm import call_llm


def parse_meeting_log(log: str) -> Dict[str, Any]:
    prompt = f"""
You are a helpful assistant that extracts structured information from meeting notes.

Given the following meeting log, extract and return a JSON object with the following fields:
1. "participants": list of names mentioned
2. "summary": a short summary (1-2 sentences)
3. "action_items": a list of action items discussed

ONLY return a valid JSON object. No explanations or formatting outside the JSON block.

Meeting Log:
\"\"\"{log}\"\"\"
"""

    response = call_llm(prompt)

    try:
        # In case model wraps it in code block
        match = response.strip()
        if match.startswith("```json"):
            match = match.removeprefix("```json").removesuffix("```").strip()
        elif match.startswith("```"):
            match = match.removeprefix("```").removesuffix("```").strip()

        return json.loads(match)
    except Exception as e:
        return {"error": f"Failed to parse JSON from LLM output: {e}", "raw_response": response}


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