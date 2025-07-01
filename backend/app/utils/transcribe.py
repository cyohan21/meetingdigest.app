from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(filepath):
    with open(filepath, "rb") as audio_file:
        print("[TRANSCRIBE] Sending file to Whisper...")
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        print("[TRANSCRIBE] Got response.")
        return response.text
