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
    temperature=0,
)

@tool
def sync_dropbox(folder: str) -> str:
    """Sync all documents from a Dropbox folder to the vector database.
    Use this when the user asks to sync, refresh, or update documents.
    Always ask the user for the folder path before calling this tool."""
    from agent.dropbox_sync import start_dropbox_sync
    start_dropbox_sync(folder)
    return f"Dropbox sync started for folder '{folder}'. All documents will be updated shortly."


@tool
def list_dropbox(folder: str) -> str:
    """List all folders and files in a Dropbox folder.
    Use this when the user wants to see what files or folders exist in Dropbox.
    Use '/' to list the root folder."""
    from agent.dropbox_sync import list_dropbox_files
    return list_dropbox_files(folder)


llm_with_tools = llm.bind_tools([sync_dropbox, list_dropbox])


def retrieve(state: State) -> dict:
    messages = state["messages"]
    recent_texts = [
        m.content for m in messages[-2:]
        if hasattr(m, "content") and isinstance(m.content, str)
    ]
    query = " ".join(recent_texts)
    retriever = get_vectorstore().as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 10, "score_threshold": 0.1},
    )
    docs = retriever.invoke(query)
    return {"context": docs}


def generate(state: State) -> dict:
    docs = state.get("context", [])
    if docs:
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "documento")
            context_parts.append(f"[{i}] Fonte: {source}\n{doc.page_content}")
        context_text = "\n\n".join(context_parts)
        context_instruction = (
            "Use APENAS o contexto numerado abaixo para responder. "
            "Se a resposta não estiver no contexto, diga que não encontrou nos materiais disponíveis. "
            "Cite o número da fonte (ex: [1]) quando usar um trecho."
        )
        context_block = f"\n\nContexto:\n{context_text}"
    else:
        context_instruction = (
            "Não há materiais específicos disponíveis para esta pergunta. "
            "Responda com base no seu conhecimento geral sobre gerenciamento de construção e projetos, "
            "deixando claro que não há documentação de suporte."
        )
        context_block = ""

    system_message = SystemMessage(
        content=(
            "Você é um assistente de ensino especializado em gerenciamento de construção e projetos. "
            f"{context_instruction} "
            "Forneça explicações claras e objetivas. "
            "Quando usar uma ferramenta e receber seu resultado, apresente-o completamente na sua resposta. "
            f"{context_block}"
        )
    )

    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("tools", ToolNode([sync_dropbox, list_dropbox]))

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_conditional_edges("generate", tools_condition)
builder.add_edge("tools", "generate")

graph = builder.compile()
