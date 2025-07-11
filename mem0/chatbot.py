from langchain_openai import ChatOpenAI
from mem0 import Memory

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.avalai.ir/v1",
    api_key="avalai-api"
)

mem = Memory.from_config({
    "llm": {
        "provider": "openai",
        "config": {
            "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
            "openai_base_url": "https://openrouter.ai/api/v1",
            "api_key": "openrouter-api"
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
