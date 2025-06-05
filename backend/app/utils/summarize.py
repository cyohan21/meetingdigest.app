from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_transcript(text):
    prompt = f"Summarize this transcript clearly and concisely:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes transcripts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()