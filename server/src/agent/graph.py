import os

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict

from agent.vectorstore import get_vectorstore


class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: list[Document]


llm = ChatOpenAI(
    model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    streaming=True,
)

@tool
def sync_dropbox(folder: str) -> str:
    """Sync all documents from a Dropbox folder to the vector database.
    Use this when the user asks to sync, refresh, or update documents.
    Always ask the user for the folder path before calling this tool."""
    from agent.dropbox_sync import start_dropbox_sync
    start_dropbox_sync(folder)
    return f"Dropbox sync started for folder '{folder}'. All documents will be updated shortly."


llm_with_tools = llm.bind_tools([sync_dropbox])


def retrieve(state: State) -> dict:
    latest_message = state["messages"][-1]
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(latest_message.content)
    return {"context": docs}


def generate(state: State) -> dict:
    context_text = "\n\n".join(doc.page_content for doc in state.get("context", []))

    system_message = SystemMessage(
        content=(
            "You are a helpful teaching assistant specialized in construction management and project management. "
            "Use the context below to answer the student's question. "
            "If the context is not relevant or not related to your specialization, say that you cannot answer based on the provided context. "
            "Provide clear and concise explanations. "
            "Responda com o idioma português\n\n"
            f"Context:\n{context_text}"
        )
    )

    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("tools", ToolNode([sync_dropbox]))

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_conditional_edges("generate", tools_condition)
builder.add_edge("tools", END)

graph = builder.compile()
