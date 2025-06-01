import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from inflect.components import Tool


# Load environment variables from .env file in this directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SLACK_URL = "https://slack.com/api/chat.postMessage"


class SlackTool(Tool):
    def __init__(self):
        super().__init__(name="Slack", function=self.send_message)

    def send_message(self, context: Dict[str, Any]) -> str:
        message = context.get("input", "")
        try:
            if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
                return "❌ SLACK_BOT_TOKEN and SLACK_CHANNEL_ID must be set in the .env file."

            payload = {
                "channel": SLACK_CHANNEL_ID,
                "text": message
            }
            headers = {
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json"
            }

            response = requests.post(SLACK_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                return f"❌ Slack API error: {data.get('error')}"

            return f"💬 Message posted to Slack channel {SLACK_CHANNEL_ID}"

        except Exception as e:
            return f"❌ Failed to post to Slack: {str(e)}"


if __name__ == "__main__":
    print("🚀 Testing Slack tool...")
    slack_tool = SlackTool()
    test_context = {"input": "Hello from the Slack tool!"}
    result = slack_tool.run(test_context)
    print("🔍 Result:", result)