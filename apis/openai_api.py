
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=API_KEY)
def get_response(query: str):
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{query}"},
                ]
        )
    
    return response.choices[0].message.content
    ...