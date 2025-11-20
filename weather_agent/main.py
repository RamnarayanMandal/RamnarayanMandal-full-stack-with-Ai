from openai import OpenAI
from dotenv import load_dotenv
from agent import SYSTEM_PROMPT
from ollama import Client
import json
import requests
import re

load_dotenv()
client = OpenAI()


ollama_client = Client(host="http://localhost:11434") 



# ----------------------------------------
# TOOL DEFINITIONS
# ----------------------------------------
def get_weather(city: str):
    """Fetch weather info using wttr.in"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Error fetching weather (HTTP {response.status_code})"
    except requests.RequestException as e:
        return f"Request failed: {e}"


# Register all tools here
available_tools = {
    "get_weather": get_weather
}


# ----------------------------------------
# SEND MESSAGE TO MODEL
# ----------------------------------------
def generate_response(message_history):
    """Send message history to OpenAI and return parsed JSON"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_history
    )

    # Correct way to extract content in new SDK
    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "step": "OUTPUT",
            "content": content
        }



def chat_with_ollama(message_history):
    response = ollama_client.chat(
        model="llama3.2",
        messages=message_history
    )

    raw = response["message"]["content"]


    json_result = raw

    if json_result is None:
        return {"error": "No valid JSON extracted", "raw": raw}

    return json_result

    
# ----------------------------------------
# MAIN LOOP
# ----------------------------------------
if __name__ == "__main__":

    message_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    user_input = input("Enter your question: ")
    message_history.append({"role": "user", "content": user_input})

    while True:

        ai_json = generate_response(message_history)
        # ai_json = chat_with_ollama(message_history)
        # print(f"\n🤖 AI RESPONSE: {ai_json}")


        # Add assistant response to history
        message_history.append({
            "role": "assistant",
            "content": json.dumps(ai_json)
        })

        step = ai_json.get("step")
        content = ai_json.get("content", "")

        # ----------------------------------------
        # STEP HANDLING
        # ----------------------------------------

        if step == "START":
            print(f"\n🟢 START: {content}")
            continue

        elif step == "PLAN":
            print(f"\n🧠 PLAN: {content}")
            continue

        elif step == "TOOL":
            tool_name = ai_json.get("tool")
            tool_input = ai_json.get("input")

            print(f"\n🔧 TOOL CALL → {tool_name}('{tool_input}')")

            # Find tool function in registry
            tool_fn = available_tools.get(tool_name)

            if tool_fn is None:
                result = f"❌ Unknown tool: {tool_name}"
            else:
                result = tool_fn(tool_input)

            # Add OBSERVE step into message history
            message_history.append({
                "role": "assistant",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "content": result
                })
            })

            continue

        elif step == "OUTPUT":
            print(f"\n✅ OUTPUT: {content}")
            break

        else:
            print(f"\n⚠️ Unknown step received: {step}")
            break
