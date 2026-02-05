from __future__ import annotations
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from agent_humancapital.config import SETTINGS

def get_chat_model(temperature: float = 0.2) -> ChatOpenAI:
    return ChatOpenAI(
        model=SETTINGS.LLM_MODEL,
        api_key=SETTINGS.OPENAI_API_KEY,
        temperature=temperature,
    )

def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=SETTINGS.EMBEDDING_MODEL,
        api_key=SETTINGS.OPENAI_API_KEY,
    )
