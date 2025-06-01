from typing import Dict, Any
from inflect_gtm.components.utils.llm import call_llm


class Agent:
    """Simple LLM-based agent class with name, instruction, and model config."""

    def __init__(
        self,
        name: str,
        instruction: str,
        model: str = "llama3.1",
        chat: bool = False,
        temperature: float = 0.2,
    ):
        """
        Initializes an agent.

        Args:
            name (str): Unique identifier for the agent.
            instruction (str): The system prompt or role for the LLM.
            model (str): Model name (e.g., llama3.1).
            chat (bool): Whether to use chat-style conversation.
            temperature (float): Sampling temperature for generation.
        """
        self.name = name
        self.instruction = instruction
        self.model = model
        self.chat = chat
        self.temperature = temperature

    def run(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Executes the agent using the given context.

        Args:
            context (Dict[str, Any]): Shared context with at least an "input" key.

        Returns:
            Dict[str, str]: Output dictionary with the agent name as the key.
        """
        input_text = context.get("input", "")
        response = call_llm(
            instruction=self.instruction,
            context=input_text,
            model=self.model,
            chat=self.chat,
            temperature=self.temperature,
        )
        return {self.name: response}


if __name__ == "__main__":
    dummy_agent = Agent(
        name="test_agent",
        instruction="You are a helpful assistant.",
        model="llama3.1",
        chat=False,
        temperature=0.0
    )

    dummy_context = {"input": "What is 2 + 2?"}
    result = dummy_agent.run(dummy_context)
    print("Test Output:", result)