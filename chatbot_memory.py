from openai import OpenAI

# Initialize with your API key
client = OpenAI(api_key="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")

# Store chat history
messages = [{"role": "system", "content": "You are a helpful English tutor."}]

print("💬 Chatbot ready! (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye 👋")
        break
     # Add user message
    messages.append({"role": "user", "content": user_input})

    # Get AI response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    bot_reply = response.choices[0].message.content
    print("AI:", bot_reply)

    # Add AI response to history
    messages.append({"role": "assistant", "content": bot_reply})