from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: list[Document]


llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory="./data/chroma",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


def retrieve(state: State) -> dict:
    latest_message = state["messages"][-1]
    docs = retriever.invoke(latest_message.content)
    return {"context": docs}


def generate(state: State) -> dict:
    context_text = "\n\n".join(doc.page_content for doc in state.get("context", []))

    system_message = SystemMessage(
        content=(
            "You are a helpful teaching assistant. "
            "Use the context below to answer the student's question. "
            "If the context is not relevant, answer from your general knowledge.\n\n"
            f"Context:\n{context_text}"
        )
    )

    response = llm.invoke([system_message] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

graph = builder.compile()
