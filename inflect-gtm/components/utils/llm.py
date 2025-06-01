import subprocess
import ollama
import json
from typing import Optional


def call_llm(
    prompt: Optional[str] = "",
    model: str = "llama3.1",
    chat: bool = False,
    temperature: float = 0.2,
    instruction: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    """
    Calls an LLM model with a given prompt, optionally using instruction and context.

    Args:
        prompt: Prompt to send (if not using instruction/context).
        model: Model to use.
        chat: Whether to use chat-based API (ollama.chat) or CLI.
        temperature: Sampling temperature.
        instruction: Instruction to prepend to the prompt.
        context: Optional dictionary to include in the prompt.

    Returns:
        Raw output string from the model.
    """
    if instruction or context:
        context_str = json.dumps(context, indent=2) if context else ""
        prompt = f"{instruction}\n\nContext:\n{context_str}".strip()

    if chat:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        return response["message"]["content"]
    else:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()