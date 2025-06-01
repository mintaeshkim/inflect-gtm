from langchain.agents import Tool
from tools.gmail.gmail_tool import send_email_tool

tool_registry = {
    "Gmail": Tool(
        name="Gmail",
        func=send_email_tool,
        description="Send an email using Gmail"
    ),
    # Add others here later
}