from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_groq_response(user_message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant like ChatGPT. Give clear and detailed answers."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.7,
            max_tokens=500
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error generating response: {str(e)}"