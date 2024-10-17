from llama_cpp import Llama
import json
import re
from typing import List, Union

from knowledge_store import MarqoKnowledgeStore

LLM = Llama(model_path="./models/7B/llama-2-7b-chat.Q4_K_M.gguf", n_ctx=2048)


def answer(user_input: str, mks: MarqoKnowledgeStore, limit: int) -> str:
    print("QUERY:", user_input)
    context = mks.query_for_content(user_input, "text", limit if limit else 5)
    print(json.dumps(context, indent=4))
    print(len(context))

    sources = "\n".join(f"[{i+1}] {source}" for i, source in enumerate(context))

    prompt = f"""
    CONTEXT:
    {sources}
    Q: {user_input} Provide detail.
    A:"""
    response = ""
    for resp in LLM(prompt, max_tokens=512, stop=["Q:"], stream=True):
        response += resp["choices"][0]["text"]
        yield resp["choices"][0]["text"].encode("utf-8")

    yield "\n## Sources\n" + sources
