from llama_cpp import Llama
import json
import re
from typing import List, Union

from knowledge_store import MarqoKnowledgeStore

# LLM = Llama(model_path="./models/7B/llama-7b.ggmlv3.q3_K_L.bin", n_ctx=2048)
LLM = Llama(
    model_path="./models/7B/Wizard-Vicuna-7B-Uncensored.ggmlv3.q4_K_M.bin", n_ctx=2048
)
# LLM = Llama(model_path="./models/13B/llama-13b.ggmlv3.q4_1.bin", n_ctx=2048)
# LLM = Llama(model_path="./models/13B/gpt4-x-alpaca-13b-ggml-q4_0.bin", n_ctx=2048)
# LLM = Llama(model_path="./models/13B/stable-vicuna-13B.ggmlv3.q3_K_L.bin", n_ctx=2048)
# LLM = Llama(model_path="./models/13B/stable-vicuna-13B.ggmlv3.q2_K.bin", n_ctx=1024)


def answer(user_input: str, mks: MarqoKnowledgeStore, limit: int) -> str:
    print("QUERY:", user_input)
    context = mks.query_for_content(user_input, "text", limit if limit else 5)
    print(json.dumps(context, indent=4))
    print(len(context))

    sources = "\n".join(f"[{i+1}] {source}" for i, source in enumerate(context))

    # prompt = f"CONTEXT: {['. '.join(context)]} Q: {user_input} A: "

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
    # used = []
    # for i in range(len(context)):
    #     if response.find(f"[{i+1}]") >= 0:
    #         used.append(f"[{i+1}] {context[i]}")
    # if used:
    #     yield "\n" + "\n".join(used)
