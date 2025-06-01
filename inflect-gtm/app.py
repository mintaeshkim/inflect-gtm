from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from tools.registry import tool_registry

# FastAPI 앱 생성
app = FastAPI(title="Agent Builder API")

# CORS 미들웨어 설정 (Next.js 프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에이전트 인스턴스 저장소
agents = {}

# 상태 변수 (Streamlit의 session_state 대체)
state = {
    "user_task": "",
    "selected_tools": [],
    "agent_executor": None,
}

# API 요청 모델
class ChatRequest(BaseModel):
    input: str

class AgentCreateRequest(BaseModel):
    task: str
    tools: List[str]

# API 응답 모델
class ChatResponse(BaseModel):
    output: str

class AgentResponse(BaseModel):
    agent: Dict[str, Any]

class ToolsResponse(BaseModel):
    tools: List[str]

class HealthResponse(BaseModel):
    status: str

# 헬스 체크 엔드포인트
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}

# 도구 목록 엔드포인트
@app.get("/api/tools", response_model=ToolsResponse)
async def get_tools():
    tools = list(tool_registry.keys())
    return {"tools": tools}

# 채팅 엔드포인트
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_input = request.input
    
    # 에이전트가 생성되었는지 확인
    if state["agent_executor"]:
        # 에이전트에 사용자 입력 전달
        result = state["agent_executor"].invoke({"input": user_input})
        return {"output": result["output"]}
    else:
        # 에이전트가 없는 경우 기본 응답
        response = f"I understand you want to know about: {user_input}. To create an agent to help with this, say 'build agent'."
        return {"output": response}

# 에이전트 생성 엔드포인트
@app.post("/api/create_agent", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest):
    try:
        state["user_task"] = request.task
        state["selected_tools"] = request.tools
        
        # 선택된 도구 객체 가져오기
        selected_tool_objs = [tool_registry[name] for name in request.tools if name in tool_registry]
        
        # 시스템 프롬프트
        system_prompt = f"You are an assistant that helps the user with the following task: {request.task}"
        
        # LangChain 에이전트 생성
        llm = ChatOllama(model="llama3.1", temperature=0, system=system_prompt)
        agent = create_react_agent(llm, selected_tool_objs)
        
        workflow = StateGraph(dict)
        workflow.add_node("agent", RunnableLambda(agent.invoke))
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)
        graph_executor = workflow.compile()
        
        # 상태 업데이트
        state["agent_executor"] = agent
        
        # 응답할 에이전트 정보
        agent_info = {
            "id": "agent-1",  # 실제로는 고유 ID 생성
            "name": request.task[:30] + "..." if len(request.task) > 30 else request.task,
            "tools": request.tools,
            "status": "ready",
            "task": request.task
        }
        
        return {"agent": agent_info}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create agent: {str(e)}"}
        )

# 앱 실행 (직접 실행 시)
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
