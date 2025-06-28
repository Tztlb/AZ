from langchain_openai import ChatOpenAI
from mem0 import MemoryClient

llm = ChatOpenAI(model="deepseek-chat", base_url="https://api.avalai.ir/v1", api_key="avalai-api")
mem = MemoryClient(api_key="mem0-api")

while True:
    user_msg = input("User: ")
    if user_msg.strip().lower() in ["exit", "quit"]:
        print(" Agent: Bye!")
        break

    memories_raw = mem.search(query=user_msg, user_id="user1", output_format="v1.1")["results"]

    memory_msgs = [{"role": "system", "content": mem["memory"]} for mem in memories_raw]

    prompt = memory_msgs + [{"role": "user", "content": user_msg}]

    resp = llm.invoke(prompt)
    print("Bot:", resp.content)

    mem.add([
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": resp.content}
    ], user_id="user1", agent_id="agent1", output_format="v1.1")