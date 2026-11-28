
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.graph import create_agent_graph
from app.security import get_current_user
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
class ChatResponse(BaseModel):
    answer: str
@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    access_token = current_user.get("raw_token")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is missing."
        )
    try:
        graph = create_agent_graph(access_token)
        system_message = SystemMessage(
            content=(
                "You are ShopStream AI Assistant. "
                "Help users with product searches and their own orders. "
                "Use the available tools when needed. "
                "Never invent product or order information. "
                "Only provide information returned by the tools."
            )
        )
        human_message = HumanMessage(
            content=request.message
        )
        initial_state = {
            "messages": [
                system_message,
                human_message
            ]
        }
        final_state = graph.invoke(initial_state)
        answer = final_state["messages"][-1].content
        if not isinstance(answer, str):
            answer = " ".join(
                block["text"]
                for block in answer
                if isinstance(block, dict) and "text" in block
            )
        return ChatResponse(answer=answer)
    except ValueError as exc:
        logger.exception("AI Assistant configuration or validation error")
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
    except Exception:
        logger.exception("AI Assistant chat execution failed")
        raise HTTPException(
            status_code=502,
            detail="AI Assistant could not process your request."
        )
