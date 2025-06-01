from inflect.components import Agent, LocalMemory, GlobalMemory
from inflect.components.utils.llm import call_llm
from inflect.tools import GoogleSheetsTool


class RootAgent(Agent):
    def __init__(self):
        super().__init__(
            name="RootAgent",
            instruction="You are the root agent responsible for orchestrating customer onboarding and communicating task progress with the user.",
            model="llama3.1",
            temperature=0.0
        )
        self.local_memory = LocalMemory()
        self.global_memory = None

    def run(self, context):
        # Fetch customer data from Google Sheets
        google_sheets_tool = GoogleSheetsTool()
        result = google_sheets_tool.fetch_and_parse(context)
        context.update(result)

        # Update memories
        self.local_memory.add("user", context.get("input", ""))
        self.local_memory.add("assistant", context.get("output", ""))
        self.global_memory.set("customers", context.get("data", []))

        # Interact with the user about task progress
        conversation_history = self.local_memory.get()
        global_memory_snapshot = self.global_memory.dump()

        summary_prompt = f"You are managing a customer onboarding process.\n\nConversation history:\n{conversation_history}\n\nShared memory:\n{global_memory_snapshot}\n\nSummarize the progress so far and ask the user if they want to add or change anything."

        update_message = call_llm(
            instruction=self.instruction,
            context={"text": summary_prompt},
            model=self.model,
            temperature=self.temperature,
            chat=True
        )
        print("\n🤖 Root Agent Summary:")
        print(update_message)

        return context


if __name__ == "__main__":
    print("🚀 Running Root Agent...")
    global_memory = GlobalMemory()
    agent = RootAgent()
    agent.global_memory = global_memory

    input_message = {"input": "sheet:customer_info; range:A1:F100"}
    result = agent.run(input_message)

    print("\n📋 Parsed Customers:")
    for customer in result.get("data", []):
        print(customer)