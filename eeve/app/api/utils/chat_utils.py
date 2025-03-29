from operator import itemgetter

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.retrievers import RetrieverOutputLike
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.base import Runnable
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.api.deps import SessionDep
from app.crud import chat_crud


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


chat_session_store = {}
retriever_store = {}


def get_chat_session_history_from_dict(chat_session_id: int) -> BaseChatMessageHistory:
    if chat_session_id not in chat_session_store:
        chat_session_store[chat_session_id] = InMemoryChatMessageHistory()
    return chat_session_store[chat_session_id]


def get_chat_session_history_from_db(
    chat_session_store: dict, db: Session, chat_session_id: int
) -> None:
    conversations = chat_crud.get_conversations(db, chat_session_id=chat_session_id)
    get_chat_session_history_from_dict(chat_session_id)
    if conversations:
        for conversation in conversations:
            if conversation.sender.value == "user":
                chat_session_store[chat_session_id].add_message(
                    HumanMessage(content=conversation.message)
                )
            elif conversation.sender.value == "bot":
                chat_session_store[chat_session_id].add_message(
                    AIMessage(content=conversation.message)
                )


def get_token_trimmer(model: ChatOllama, max_tokens: int) -> list[BaseMessage]:
    return trim_messages(
        max_tokens=max_tokens,
        strategy="last",
        token_counter=model,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )


def load_and_split_documents(
    pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[str]:
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)
    return splits


def create_vectorstore_and_retriever(splits: list[str]) -> VectorStoreRetriever:
    vectorstore = Chroma.from_documents(
        documents=splits, embedding=HuggingFaceBgeEmbeddings()
    )
    return vectorstore.as_retriever()


def create_history_aware_retriever_chain(
    llm: ChatOllama, retriever: VectorStoreRetriever
) -> RetrieverOutputLike:
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever


def create_question_answer_chain(llm: ChatOllama) -> Runnable:
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    return question_answer_chain


def create_rag_chain(llm: ChatOllama, retriever: VectorStoreRetriever) -> Runnable:
    question_answer_chain = create_question_answer_chain(llm)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain


async def ensure_chat_session_initialized(chat_session_id: int, db: SessionDep) -> str:
    if (
        chat_session_id not in chat_session_store
        or not chat_session_store[chat_session_id].messages
    ):
        get_chat_session_history_from_db(chat_session_store, db, chat_session_id)
        return "initialized"
    return ""


def create_chain_with_trimmer(
    token_trimmer: list[BaseMessage], prompt: str, llm: ChatOllama
) -> Runnable:
    chain = (
        RunnablePassthrough.assign(messages=itemgetter("messages") | token_trimmer)
        | prompt
        | llm
    )
    return chain


def get_prompt() -> ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt


def get_llm() -> ChatOllama:
    llm = ChatOllama(model="EEVE-Korean-10.8B:latest")
    return llm
