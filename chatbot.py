from openai import OpenAI

# Initialize OpenAI
client = OpenAI(api_key="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")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye! 👋")
        break

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}]
    )

    print("AI:", response.choices[0].message.content)