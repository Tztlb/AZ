import subprocess  
import json       

def query_gpt4(conversation_history):
    api_key = "api"  
    domain = "domain"
    endpoint = f"{domain}/chat/completions"
    
    headers = [
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json"
    ]
    

    data = json.dumps({
        "model": "gpt-4",
        "messages": conversation_history, 
        "temperature": 0.7
    })
    

    curl_cmd = ["curl", "-s", "-X", "POST", endpoint] + headers + ["-d", data]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        return response.get("choices", [{}])[0].get("message", {})  
    except subprocess.CalledProcessError as e:
        return {"role": "assistant", "content": "Error: Request failed. Details: " + str(e)}
    except json.JSONDecodeError:
        return {"role": "assistant", "content": "Error: Invalid JSON response."}

if __name__ == "__main__":
    conversation_history = []  
    print("Chatbot: Hello! Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})

        response = query_gpt4(conversation_history)

        conversation_history.append(response)
        print(f"Chatbot: {response.get('content', 'Error occurred')}")
