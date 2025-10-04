"""
Voice Tutor (press Enter to record) - Simple end-to-end proof-of-concept

Features:
- Press Enter to START recording, speak, then press Enter again to STOP.
- Saves recorded audio to input.wav
- Sends audio to OpenAI Whisper (Audio Transcription API)
- Sends transcribed text to ChatGPT (correction + short explanation)
- Speaks the ChatGPT reply using pyttsx3
- Appends the conversation to conversations.json (timestamp, user_text, ai_reply)

Requirements: Python 3.8+ and an OpenAI API key set in environment variable OPENAI_API_KEY.
See the included README for installation and usage steps.
"""

import os
import time
import json
import datetime
import sounddevice as sd
import soundfile as sf
import openai
import pyttsx3

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("Please set your OpenAI API key in the environment variable OPENAI_API_KEY.\n"
                    "On Windows (PowerShell): setx OPENAI_API_KEY \"sk-...\"\n"
                    "On Linux/macOS (bash): export OPENAI_API_KEY=\"sk-...\"")

openai.api_key = OPENAI_API_KEY

AUDIO_FILENAME = "input.wav"
CONVERSATIONS_FILE = "conversations.json"
SAMPLERATE = 16000
CHANNELS = 1

def record_until_enter(filename=AUDIO_FILENAME, samplerate=SAMPLERATE, channels=CHANNELS):
    print("\\n== Voice Tutor: Recording (press Enter) ==")
    input("Press Enter to START recording...")
    print("Recording... Speak now. Press Enter to STOP recording.")
    # Open sound file and input stream; write frames in callback until Enter pressed
    try:
        with sf.SoundFile(filename, mode='w', samplerate=samplerate, channels=channels, subtype='PCM_16') as file:
            with sd.InputStream(samplerate=samplerate, channels=channels, callback=lambda indata, frames, time_info, status: file.write(indata.copy())):
                input()  # wait until user presses Enter to stop
    except Exception as e:
        print("Error during recording:", e)
        raise
    print(f"Saved recording to {filename}")


def transcribe_with_whisper(filename=AUDIO_FILENAME):
    print("\\n-> Transcribing with Whisper (OpenAI)... (this uses your OpenAI API key and may incur costs)")
    try:
        with open(filename, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        text = transcript.get("text", "").strip()
        print("Transcript:", text)
        return text
    except Exception as e:
        print("Error during transcription:", e)
        return ""


def chat_correct_and_reply(user_text):
    if not user_text.strip():
        return "I couldn't understand what you said. Please try again."
    prompt = (
        "You are an English tutor. The user spoke a sentence. "
        "Reply with: 1) a corrected version of the sentence, 2) a one-sentence simple explanation, "
        "3) a short encouraging line. Return the three parts separated clearly (use new lines)."
        f"\\n\\nUser said: \"{user_text}\""
    )
    print("\\n-> Sending to ChatGPT for correction and feedback...")
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=200,
            temperature=0.2
        )
        reply = resp["choices"][0]["message"]["content"].strip()
        print("Tutor reply:\\n", reply)
        return reply
    except Exception as e:
        print("Error while contacting ChatGPT:", e)
        return "Sorry, I couldn't process that right now."


def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS error:", e)
        print("Reply (text):", text)


def save_conversation(user_text, ai_reply, filename=CONVERSATIONS_FILE):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "user_text": user_text,
        "ai_reply": ai_reply
    }
    data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(entry)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Could not save conversations file:", e)


def main():
    print("=== Voice Tutor (Press-Enter Recording) ===")
    print("Make sure your microphone is connected and your OPENAI_API_KEY is set as an environment variable.\n")
    while True:
        record_until_enter()
        user_text = transcribe_with_whisper()
        if not user_text:
            print("No text detected or transcription failed. Try again.\\n")
            cont = input("Do you want to try again? (y/n): ").strip().lower()
            if cont == "y":
                continue
            else:
                break
        ai_reply = chat_correct_and_reply(user_text)
        save_conversation(user_text, ai_reply)
        speak_text(ai_reply)
        print("\\n--- Conversation saved. ---\\n")
        again = input("Do another recording? (y/n): ").strip().lower()
        if again != "y":
            print("Exiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
