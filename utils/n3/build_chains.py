from typing import Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import OllamaLLM


def build_chains(
    llm: OllamaLLM,
    templates: Dict[str, str],
) -> Dict[str, RunnableSerializable[Dict[str, str], str]]:
    chains: Dict[str, RunnableSerializable[Dict[str, str], str]] = {}
    for key, template in templates.items():
        prompt = ChatPromptTemplate.from_template(template)
        chains[key] = prompt | llm
    return chains
