from inflect_gtm.components import Agent, LocalMemory, GlobalMemory
from inflect_gtm.tools.gmail.gmail_tool import GmailTool
from inflect_gtm.tools.google_calendar.google_calendar_tool import GoogleCalendarTool
from inflect_gtm.components.utils.meeting_log_parser import parse_meeting_log
from inflect_gtm.components.utils.llm import call_llm
from inflect_gtm.components.utils.rag_prompt_builder import build_followup_prompt


class PostDemoFollowupAgent(Agent):
    def __init__(self):
        super().__init__(
            name="post_demo_agent",
            instruction="You are a follow-up assistant that generates and sends personalized emails after product demo meetings.",
            model="llama3.1",
            temperature=0.4,
            chat=False
        )
        self.local_memory = LocalMemory()
        self.global_memory = None
        self.gmail_tool = GmailTool()
        self.calendar_tool = GoogleCalendarTool()

    def run(self, context):
        # Step 1: Parse meeting log using LLM
        raw_log = context.get("meeting_log", "")
        parsed = parse_meeting_log(raw_log)
        self.local_memory.add("user", raw_log)
        self.local_memory.add("assistant", str(parsed))
        self.global_memory.set("meeting_summary", parsed)

        # Step 2: Fetch calendar events for additional context
        events_result = self.calendar_tool.get_upcoming_events({"n": 3})
        events = events_result.get("events", [])
        self.global_memory.set("upcoming_events", events)

        # Step 3: Generate follow-up email using prompt builder
        context["user_name"] = context.get("user_name", "Mintae Kim")
        prompt = build_followup_prompt({
            "meeting_log": parsed,
            "calendar_events": events,
            "user_name": context["user_name"]
        })

        llm_response = call_llm(prompt)
        self.local_memory.add("user", prompt)
        self.local_memory.add("assistant", llm_response)

        # Step 4: Parse and send the email
        try:
            lines = llm_response.strip().splitlines()
            subject_line = next((line for line in lines if line.lower().startswith("subject:")), None)

            if subject_line:
                subject = subject_line.split(":", 1)[1].strip()
                body = "\n".join(line for line in lines if not line.lower().startswith("subject:")).strip()
            else:
                subject = "Follow-up on recent meeting"
                body = llm_response.strip()

            # Clean body (remove undesired prefix like "Here is a professional follow-up email:")
            if body.lower().startswith("here is a professional follow-up email"):
                body = body.split("\n", 1)[-1].strip()

            to = context.get("to", "")
            if not to:
                raise ValueError("No recipient email address provided in context.")

            send_result = self.gmail_tool.send_email({
                "input": f"to:{to}; subject:{subject}; body:{body}"
            })

            print("📧 Email Sent:", send_result)
            self.global_memory.set("emails_sent", send_result)
        except Exception as e:
            print("❌ Failed to send email:", str(e))
            subject, body = None, None

        return {
            "summary": parsed.get("summary", ""),
            "email_subject": subject,
            "email_body": body
        }


if __name__ == "__main__":
    print("🚀 Running Post-Demo Follow-Up Agent...")
    global_memory = GlobalMemory()
    agent = PostDemoFollowupAgent()
    agent.global_memory = global_memory

    # Simulated context
    context = {
        "meeting_log": """
Met with Sarah and James to discuss the new onboarding flow. 
Sarah asked for a demo of the integrations and seemed excited about the Slack integration.
James requested a follow-up on pricing tiers. 
Next steps: send them the latest slide deck and book a call with technical support.
""",
        "to": "customer@example.com",
        "user_name": "Mintae Kim"
    }

    result = agent.run(context)

    print("\n📬 Email Output:")
    print("Subject:", result.get("email_subject"))
    print("Body:\n", result.get("email_body"))