from inflect.components import Agent, LocalMemory, GlobalMemory
from inflect.tools import GoogleSheetsTool
import json
import re


class AnalystAgent(Agent):
    def __init__(self):
        super().__init__(
            name="analyst",
            instruction="You are an analyst agent. Given a list of customers, you will write a Python function to segment them based on key attributes, and generate onboarding strategies for each segment.",
            model="llama3.1",
            temperature=0.3,
            chat=False
        )
        self.local_memory = LocalMemory()
        self.global_memory = None

    def run(self, context):
        customers = context.get("data", [])
        sample_customers = customers[:5]  # Only use sample for prompt
        customer_json = json.dumps(sample_customers, indent=2)

        # Step 1: Generate segmentation function
        code_prompt = f"""
You are given a few example customer records in JSON:

{customer_json}

Write a Python function called `segment_customers(customers: list[dict]) -> dict` that segments customers into logical groups.
Group by patterns in fields like 'Company Size', 'Department', or others.
Return only the full function inside a Python code block.
"""
        try:
            context["input"] = code_prompt
            response = super().run(context)
            code_response = response[self.name]
            self.local_memory.add("user", code_prompt)
            self.local_memory.add("assistant", code_response)

            match = re.search(r"```python\n(.*?)```", code_response, re.DOTALL)
            if not match:
                raise ValueError("No Python code block found in code response.")
            code = match.group(1)
            print("✅ Code generation successful.")
            self.global_memory.set("segment_function_code", code)
        except Exception as e:
            print("\n❌ Code generation failed:", str(e))
            return context

        # Step 2: Generate strategies
        strategy_prompt = f"""
You are given a few example customer records in JSON:

{customer_json}

Based on your segmentation logic in the function `segment_customers(customers)`, 
create a dictionary named `strategies` that maps each segment name to an onboarding strategy.
Return only the dictionary.
"""
        try:
            context["input"] = strategy_prompt
            response = super().run(context)
            strategy_response = response[self.name]
            self.local_memory.add("user", strategy_prompt)
            self.local_memory.add("assistant", strategy_response)

            print("\n Raw strategy response:\n", strategy_response)

            strategies_match = re.search(r"\{[\s\S]*\}", strategy_response)
            if not strategies_match:
                raise ValueError("No strategies dictionary found in strategy response.")

            strategy_text = strategies_match.group(0).strip()
            strategies = json.loads(strategy_text.replace("'", '"'))
            print("✅ Strategy generation successful.")
            self.global_memory.set("strategies", strategies)
        except Exception as e:
            print("\n❌ Strategy generation failed:", str(e))
            return context

        # Step 3: Execute code and segment customers
        try:
            exec_globals = {}
            exec(code, exec_globals)
            segment_func = exec_globals["segment_customers"]
            segments = segment_func(customers)
            self.global_memory.set("segments", segments)

            print("\n📂 Segmented Customers:")
            for seg, group in segments.items():
                print(f"\n[{seg}] - {len(group)} customers")
                for cust in group[:3]:
                    print(f"- {cust['Name']} ({cust['Company']})")

            print("\n📘 Strategies:")
            for seg, strat in strategies.items():
                print(f"\n[{seg}]: {strat}")
        except Exception as e:
            print("\n❌ Execution or segmentation failed:", str(e))

        return context


if __name__ == "__main__":
    print("🚀 Running Analyst Agent...")
    global_memory = GlobalMemory()
    agent = AnalystAgent()
    agent.global_memory = global_memory

    context = {"input": "sheet:customer_info; range:A1:F100"}
    context.update(GoogleSheetsTool().fetch_and_parse(context))

    result = agent.run(context)