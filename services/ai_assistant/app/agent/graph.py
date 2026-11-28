
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.agent.tools import (
    create_get_my_orders_tool,
    search_products
)
from app.config import settings


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def create_agent_graph(access_token: str):
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured.")

    tools = [
        search_products,
        create_get_my_orders_tool(access_token)
    ]

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=settings.GROQ_API_KEY,
        temperature=0.2
    )

    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: AgentState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]

        if last_message.tool_calls:
            return "tools"

        return END

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("agent", call_model)
    graph_builder.add_node("tools", ToolNode(tools))

    graph_builder.set_entry_point("agent")

    graph_builder.add_conditional_edges(
        "agent",
        should_continue
    )
    graph_builder.add_edge("tools", "agent")

    return graph_builder.compile()
