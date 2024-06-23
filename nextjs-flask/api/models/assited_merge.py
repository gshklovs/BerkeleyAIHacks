import os
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from llama_index.graph_stores.nebula import NebulaGraphStore
from llama_index.core import StorageContext
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever

os.environ["GROQ_API_KEY"] = "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"

llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])

def assistive_merge(paragraphs):
    merge_prompt = "\n%%%\n".join(paragraphs)
    response = llm.chat(
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content=f"Merge the following text segments delimited by (%%%):\n{merge_prompt}")
        ]
    )
    merged_text = response.message.content.replace("assistant: ", "").strip()
    return merged_text
