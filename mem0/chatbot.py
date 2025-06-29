from langchain_openai import ChatOpenAI
from mem0 import Memory

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.avalai.ir/v1",
    api_key="aa-UN4ZmttvrbXe3cBIwbQrraPzA0EOP2MJpx0tzmnFmlk12IIx"
)

mem = Memory.from_config({
    "llm": {
        "provider": "openai",
        "config": {
            "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
            "openai_base_url": "https://openrouter.ai/api/v1",
            "api_key": "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"
        }
    },
    "vector_store": {
       "provider": "chroma",
       "config": {"path": "./mem0_chroma"},
       "filter_key": ["user_id", "agent_id"]
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "./my_local_model"
        }
    }
})

while True:
    user_msg = input("User: ")
    if user_msg.strip().lower() in ["exit", "quit"]:
        print(" Agent: Bye! 👋")
        break

    memories_raw = mem.search(query=user_msg, user_id="user1")["results"]

    memory_msgs = [{"role": "system", "content": mem["memory"]} for mem in memories_raw]

    prompt = memory_msgs + [{"role": "user", "content": user_msg}]

    resp = llm.invoke(prompt)
    print("Bot:", resp.content)

    mem.add([
    {"role": "user", "content": user_msg},
    {"role": "assistant", "content": resp.content}
], user_id="user1")  
