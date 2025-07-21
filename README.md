# Inflect-GTM

End-to-End GTM (Go-to-Market) Agent project.

This project provides a framework for building and running autonomous agents to automate Go-to-Market tasks. It includes a multi-agent system for customer onboarding and a FastAPI server for dynamically creating and managing agents.

## Features

- **Multi-Agent System**: A system of specialized agents working together to achieve a common goal.
  - `RootAgent`: Orchestrates the customer onboarding process.
  - `AnalystAgent`: Analyzes data and provides insights.
  - `DocumentWriterAgent`: Generates documents.
  - `PostDemoAgent`: Handles post-demo follow-ups.
- **Dynamic Agent Creation**: A FastAPI server allows for the creation of agents with specific tasks and tools at runtime.
- **Tool Integration**: Agents can use various tools to interact with external services:
  - Google Workspace: Gmail, Google Docs, Google Sheets, Google Calendar
  - Slack
- **Memory Management**: Agents maintain both local and global memory to keep track of conversations and shared data.
- **LLM Integration**: Utilizes large language models like `llama3.1` for natural language understanding and generation.

## Project Structure

```
inflect-gtm/
├── inflect_gtm/
│   ├── agents/
│   │   ├── root_agent.py
│   │   ├── analyst_agent.py
│   │   ├── document_writer_agent.py
│   │   └── post_demo_agent.py
│   ├── components/
│   │   ├── agent/
│   │   ├── memory/
│   │   └── ...
│   ├── tools/
│   │   ├── gmail/
│   │   ├── google_docs/
│   │   └── ...
│   └── app.py
├── requirements.txt
└── pyproject.toml
```

## Getting Started

### Prerequisites

- Python 3.8+
- Pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/inflect-gtm.git
   cd inflect-gtm
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables. Create a `.env` file in the root directory and add the necessary API keys and credentials for Google Workspace and other services.

### Running the FastAPI Server

The FastAPI server allows you to create and interact with agents through a REST API.

1. Start the server:
   ```bash
   uvicorn inflect_gtm.app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. The API documentation will be available at `http://localhost:8000/docs`.

### Running the Multi-Agent System

To run the multi-agent system for customer onboarding:

```bash
python -m inflect_gtm.agents.root_agent
```

## API Endpoints

The FastAPI server provides the following endpoints:

- `GET /api/health`: Health check.
- `GET /api/tools`: Get a list of available tools.
- `POST /api/create_agent`: Create a new agent with a specific task and tools.
- `POST /api/chat`: Interact with the created agent.

### Example: Creating and using an agent

1.  **Create an agent**

    Send a `POST` request to `/api/create_agent` with the following payload:

    ```json
    {
      "task": "Summarize the latest customer feedback from Gmail",
      "tools": ["gmail_tool"]
    }
    ```

2.  **Chat with the agent**

    Send a `POST` request to `/api/chat` with your input:

    ```json
    {
      "input": "What is the overall sentiment of the feedback?"
    }
    ```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
