from openai import OpenAI
from dotenv import load_dotenv
from agent import SYSTEM_PROMPT
from pydantic import BaseModel, Field
from typing import Optional
import json
import requests
import os

load_dotenv()
client = OpenAI()


# ---------------------------------------------------------
# Pydantic Output Format
# ---------------------------------------------------------
class MyOutputFormat(BaseModel):
    step: str = Field(..., description="START, PLAN, TOOL, OBSERVE, OUTPUT")
    content: Optional[str] = Field(None, description="Content associated with the step")
    tool: Optional[str] = Field(None, description="Tool to be used")
    input: Optional[str] = Field(None, description="Input for the tool")


# ---------------------------------------------------------
# TOOL DEFINITIONS
# ---------------------------------------------------------
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

def run_command(command: str):
    """Run a shell command and return its output"""
    try:
        result = os.popen(command).read()
        return result if result else "No output"
    except Exception as e:
        return f"Command execution failed: {e}"
    

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}


# ---------------------------------------------------------
# AI CALL
# ---------------------------------------------------------
def generate_response(message_history):
    """Send message to LLM and parse using Pydantic"""
    response = client.chat.completions.parse(
        model="gpt-4o",
        messages=message_history,
        response_format=MyOutputFormat
    )

    # Model output (parsed as Pydantic)
    return response.choices[0].message.parsed


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
def main():

    while True:
        message_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        user_input = input("Enter your question: ")
        message_history.append({"role": "user", "content": user_input})

        while True:
            ai_json = generate_response(message_history)

            # Add assistant message into history
            message_history.append({
                "role": "assistant",
                "content": json.dumps(ai_json.model_dump())
            })

            step = ai_json.step
            content = ai_json.content

            # -------------------------------------------------
            # STEP HANDLING
            # -------------------------------------------------

            if step == "START":
                print(f"\n🟢 START: {content}")
                continue

            elif step == "PLAN":
                print(f"\n🧠 PLAN: {content}")
                continue

            elif step == "TOOL":
                tool_name = ai_json.tool
                tool_input = ai_json.input

                print(f"\n🔧 TOOL CALL → {tool_name}('{tool_input}')")

                tool_fn = available_tools.get(tool_name)

                if not tool_fn:
                    result = f"❌ Unknown tool: {tool_name}"
                else:
                    result = tool_fn(tool_input)

                # Add OBSERVE to history
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


# Run the program
if __name__ == "__main__":
    main()
