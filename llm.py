import subprocess
import json

def query_gpt4(prompt):
    api_key = "api"
    domain = "domain"
    endpoint = f"{domain}/chat/completions"
    
    headers = [
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json"
    ]
    
    data = json.dumps({
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    })
    
    curl_cmd = ["curl", "-s", "-X", "POST", endpoint] + headers + ["-d", data]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        return response
    except subprocess.CalledProcessError as e:
        return {"error": "Request failed", "details": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw_response": result.stdout}

if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    response = query_gpt4(prompt)
    print(json.dumps(response, indent=4))
