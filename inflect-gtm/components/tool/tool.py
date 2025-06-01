from typing import Dict, Any, Callable


class Tool:
    """
    Tool class for deterministic functions usable by agents.
    This is the parent class for all tools (e.g., Gmail, Google Docs).
    """

    def __init__(self, name: str, function: Callable[[Dict[str, Any]], Any]):
        """
        Initializes the tool.

        Args:
            name (str): Name of the tool.
            function (Callable): A callable that takes context and returns output.
        """
        self.name = name
        self.function = function

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool.

        Args:
            context (Dict[str, Any]): Shared input.

        Returns:
            Dict[str, Any]: Output with tool name as key.
        """
        output = self.function(context)
        return {self.name: output}


# Unit test
if __name__ == "__main__":
    def dummy_tool_function(context):
        return f"Echo: {context.get('input', '')}"

    echo_tool = Tool(name="echo_tool", function=dummy_tool_function)
    result = echo_tool.run({"input": "Hello from test"})
    print("Tool Output:", result)