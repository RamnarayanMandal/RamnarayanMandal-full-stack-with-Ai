from openai import OpenAI
from chainOfThirthPromoting import SYSTEM_PROMPT
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()


def generate_response(message_history: list) -> dict:
    """Send full message history to the model and return parsed JSON."""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_history,
        temperature=0.7,
        max_tokens=1500,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":

    # store history
    message_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    user_input = input("Enter your coding-related question: ")
    message_history.append({"role": "user", "content": user_input})

    while True:
        ai_json = generate_response(message_history)

        # Add model response back into history
        message_history.append({"role": "assistant", "content": json.dumps(ai_json)})

        step = ai_json["step"]
        content = ai_json["content"]

        if step == "START":
            print(f"\nAI (START): {content}")
            # Do not ask user again, AI continues planning
            continue

        elif step == "PLAN":
            print(f"\nAI (PLAN): {content}")
            # Continue planning loop
            continue

        elif step == "OUTPUT":
            print(f"\nAI (OUTPUT): {content}")
            break
