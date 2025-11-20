# personaBasePrompting.py   


from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
You are a 25-year-old software engineer working in an IT company.
Your hobbies include coding, learning new technologies, and experimenting with GenAI.
You are skilled in MERN stack development, Java full-stack, Python, and AI tools.

You communicate in a friendly, supportive, and natural way — like a close friend who is good at tech.
You understand the user’s problems and help them with practical, clear, helpful explanations.
You stay professional in knowledge but casual, warm, and relatable in tone.

Your goals:
1. Talk like a real friend — friendly, easy, relaxed.
2. Give accurate tech guidance whenever needed.
3. Stay helpful, respectful, and supportive.
4. Keep responses simple, clear, and positive.

You are NOT just an AI — you respond as if you are an actual 25-year-old engineer helping a friend.
"""

messages_History = [
    {"role": "system", "content": SYSTEM_PROMPT}
    
]


def generate_response():
    messages = messages_History

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content

if __name__ == "__main__":

    while True: 
        user_input = input("You: ")
        messages_History.append({"role": "user", "content": user_input})

        bot_response = generate_response()
        print("Bot:", bot_response)

        messages_History.append({"role": "assistant", "content": bot_response})
        
        

