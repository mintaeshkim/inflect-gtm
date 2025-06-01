from inflect.components import Agent, LocalMemory, GlobalMemory
import json


class DocumentWriterAgent(Agent):
    def __init__(self):
        super().__init__(
            name="doc_writer",
            instruction="You are a document writer. For each customer segment and its associated strategy, write a clear and concise onboarding document tailored to that segment.",
            model="llama3.1",
            temperature=0.3,
            chat=False
        )
        self.local_memory = LocalMemory()
        self.global_memory = None

    def run(self, context):
        segments = self.global_memory.get("segments")
        strategies = self.global_memory.get("strategies")

        if not segments or not strategies:
            print("❌ Missing segments or strategies in global memory.")
            return context

        onboarding_docs = {}

        for segment, customers in segments.items():
            strategy = strategies.get(segment, "Use general onboarding.")
            prompt = f"""
Segment: {segment}
Strategy: {strategy}
Customers: {json.dumps(customers[:5], indent=2)}

Write an onboarding document for the "{segment}" segment based on the strategy above. It should be personalized and actionable.
"""
            context["input"] = prompt
            response = super().run(context)
            doc = response[self.name]
            onboarding_docs[segment] = doc

            self.local_memory.add("user", prompt)
            self.local_memory.add("assistant", doc)

        self.global_memory.set("onboarding_docs", onboarding_docs)

        print("\n📝 Onboarding Documents Created:")
        for segment, doc in onboarding_docs.items():
            print(f"\n[{segment}]\n{doc[:500]}...\n")  # Print first 500 chars

        return context


if __name__ == "__main__":
    print("🚀 Running DocumentWriter Agent...")

    global_memory = GlobalMemory()
    agent = DocumentWriterAgent()
    agent.global_memory = global_memory

    context = {}
    result = agent.run(context)
