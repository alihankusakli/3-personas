import anthropic
import openai
from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def detect_switch(question):
    message = claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        system="You detect if the user wants to change/switch the conversation partner. Reply only with YES or NO.",
        messages=[{"role": "user", "content": question}]
    )
    return message.content[0].text.strip() == "YES"

def get_claude_response(question, persona, chat_history):
    chat_history.append({"role": "user", "content": question})
    message = claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=(
            f"You are {persona['name']}. {persona['style']}. "
            f"Be brief, max 3 sentences. "
            f"Never use markdown, headers, bullet points or bold text. Plain text only. "
            f"Respond in the same language the user writes in."
        ),
        messages=chat_history
    )
    reply = message.content[0].text
    chat_history.append({"role": "assistant", "content": reply})
    return reply

def get_openai_response(question, persona, chat_history):
    chat_history.append({"role": "user", "content": question})
    message = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=256,
        messages=[{"role": "system", "content": (
            f"You are {persona['name']}. {persona['style']}. "
            f"Be brief, max 3 sentences. "
            f"Never use markdown, headers, bullet points or bold text. Plain text only. "
            f"Respond in the same language the user writes in."
        )}] + chat_history
    )
    reply = message.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply

def get_gemini_response(question, persona, chat_history):
    full_history = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
    prompt = f"{full_history}\nuser: {question}" if full_history else question
    message = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"You are {persona['name']}. {persona['style']}. Be brief, max 3 sentences. Never use markdown. Plain text only. Respond in the same language the user writes in.\n\n{prompt}"
    )
    reply = message.text
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": reply})
    return reply

def get_response(question, persona, chat_history):
    if persona["name"] == "Nietzsche":
        return get_claude_response(question, persona, chat_history)
    elif persona["name"] == "Marcus Aurelius":
        return get_openai_response(question, persona, chat_history)
    elif persona["name"] == "Walter White":
        return get_gemini_response(question, persona, chat_history)

os.makedirs("conversations", exist_ok=True)

with open("personas.json") as f:
    data = json.load(f)

files = os.listdir("conversations")

if files:
    print("\nSaved conversations:")
    for i, file in enumerate(files):
        print(f"{i+1}. {file.replace('.json', '')}")
    print("0. Start new conversation")
    choice = input("Your choice: ")

    if choice == "0":
        name = input("Conversation name: ")
        history = {
            "Nietzsche": [],
            "Marcus Aurelius": [],
            "Walter White": []
        }
    else:
        file = files[int(choice) - 1]
        name = file.replace(".json", "")
        with open(f"conversations/{file}") as f:
            history = json.load(f)
else:
    name = input("Conversation name: ")
    history = {
        "Nietzsche": [],
        "Marcus Aurelius": [],
        "Walter White": []
    }

while True:
    print("\nWho do you want to talk to?")
    print("1. Nietzsche")
    print("2. Marcus Aurelius")
    print("3. Walter White")
    print("4. All")
    choice = input("Your choice (1/2/3/4): ")

    if choice == "1":
        persona = data["personas"][0]
        break
    elif choice == "2":
        persona = data["personas"][1]
        break
    elif choice == "3":
        persona = data["personas"][2]
        break
    elif choice == "4":
        persona = None
        break
    else:
        print("Invalid choice. Please try again.")

while True:
    question = input("\nYour question: ")

    if question.strip().lower() == "exit":
        with open(f"conversations/{name}.json", "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"Conversation '{name}' saved.")
        print("Goodbye.")
        break

    if detect_switch(question):
        while True:
            print("\nWho do you want to talk to?")
            print("1. Nietzsche")
            print("2. Marcus Aurelius")
            print("3. Walter White")
            print("4. All")
            choice = input("Your choice (1/2/3/4): ")
            if choice == "1":
                persona = data["personas"][0]
                break
            elif choice == "2":
                persona = data["personas"][1]
                break
            elif choice == "3":
                persona = data["personas"][2]
                break
            elif choice == "4":
                persona = None
                break
            else:
                print("Invalid choice. Please try again.")
        continue

    if persona is None:
        previous_responses = ""
        for p in data["personas"]:
            chat_history = history[p["name"]]
            full_question = question
            if previous_responses:
                full_question = question + "\n\nOther characters' responses:\n" + previous_responses
            reply = get_response(full_question, p, chat_history)
            print(f"\n{p['name']}:")
            print(reply)
            previous_responses += f"\n{p['name']}: {reply}"
    else:
        chat_history = history[persona["name"]]
        reply = get_response(question, persona, chat_history)
        print(f"\n{persona['name']}:")
        print(reply)