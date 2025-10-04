from openai import OpenAI
import speech_recognition as sr
import pyttsx3

# Initialize client with your key
client = OpenAI(api_key="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")  # 👈 put your real key here

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Say something...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return "Sorry, I didn't catch that."

while True:
    user_input = listen()
    if user_input.lower() in ["exit", "quit"]:
        speak("Goodbye!")
        break

    print(f"You said: {user_input}")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        bot_reply = f"⚠️ Error with AI: {str(e)}"

    print(f"Bot: {bot_reply}")
    speak(bot_reply)