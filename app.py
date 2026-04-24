import anthropic
from dotenv import load_dotenv
import os 
import json

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("personas.json") as f:
    data = json.load(f)
os.makedirs("sohbetler", exist_ok=True)

dosyalar = os.listdir("sohbetler")

if dosyalar:
    print("\nSaved conversations:")
    for i, dosya in enumerate(dosyalar):
        print(f"{i+1}. {dosya.replace('.json', '')}")
    print("0. Start new conversation")
    secim = input("Your choice: ")
    
    if secim == "0":
        isim = input("Conversation name: ")
        gecmisler = {
            "Nietzsche": [],
            "Marcus Aurelius": [],
            "Walter White": []
        }
    else:
        dosya = dosyalar[int(secim) - 1]
        isim = dosya.replace(".json", "")
        with open(f"sohbetler/{dosya}") as f:
            gecmisler = json.load(f)
else:
    isim = input("Conversation name")

def degistir_mi(soru):
    mesaj = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        system="You detect if the user wants to change/switch the conversation partner. Reply only with YES or NO.",
        messages=[{"role": "user", "content": soru}]
    )
    return mesaj.content[0].text.strip() == "YES"

def persona_cevap(soru, persona, gecmis):
    gecmis.append({"role": "user", "content": soru})
    mesaj = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=(
            f"You are {persona['name']}. {persona['style']}. Respond in Turkish. "
            f"Be brief, max 3 sentences. "
            f"Never use markdown, headers, bullet points or bold text. Plain text only. "
            f"You are in a philosophical conversation with Nietzsche, Marcus Aurelius, and Walter White. "
            f"You know who the others are and what they stand for. You can agree or disagree with them."
            f"When referencing other personas, only do so if their actual response is directly relevant. Never fabricate or assume what they said."
            f"Only reference another persona if you have actually seen their response in this conversation. Never assume or fabricate what they might say."
            f"If the user asks to change or switch the persona in any language, treat it as a change request and respond only with the word 'CHANGE'."
        ),
        messages=gecmis
    )
    cevap = mesaj.content[0].text
    gecmis.append({"role": "assistant", "content": cevap})
    return cevap
gecmisler = {
    "Nietzsche": [],
    "Marcus Aurelius": [],
    "Walter White": []
}

print("\nWho do you want to talk to?")
print("1. Nietzsche")
print("2. Marcus Aurelius")
print("3. Walter White")
print("4. All")
secim = input("Your choice (1/2/3/4): ")

if secim == "1":
    persona = data["personas"][0]
elif secim == "2":
    persona = data["personas"][1]
elif secim == "3":
    persona = data["personas"][2]
elif secim == "4":
    persona = None  # hepsi demek
else:
    print("Invalid choice.")
    exit()

while True:
    soru = input("Your question: ")

    if soru.strip().lower() == "exit":
        with open(f"sohbetler/{isim}.json", "w") as f:
            json.dump(gecmisler, f, ensure_ascii=False, indent=2)
        print(f"Conversation '{isim}' saved.")
        print("Goodbye.")
        break

    if degistir_mi(soru):
        print("\nWho do you want to talk to?")
        print("1. Nietzsche")
        print("2. Marcus Aurelius")
        print("3. Walter White")
        print("4. All")
        secim = input("Your choice (1/2/3/4): ")
        if secim == "1":
            persona = data["personas"][0]
        elif secim == "2":
            persona = data["personas"][1]
        elif secim == "3":
            persona = data["personas"][2]
        elif secim == "4":
            persona = None
        continue

    if persona is None:
        onceki_cevaplar = ""
        for p in data["personas"]:
            gecmis = gecmisler[p["name"]]
            tam_soru = soru
            if onceki_cevaplar:
                tam_soru = soru + "\n\nDiğer karakterlerin bu soruya verdikleri cevaplar:\n" + onceki_cevaplar
            cevap = persona_cevap(tam_soru, p, gecmis)
            print(f"\n{p['name']}:")
            print(cevap)
            onceki_cevaplar += f"\n{p['name']}: {cevap}"
    else:
        gecmis = gecmisler[persona["name"]]
        cevap = persona_cevap(soru, persona, gecmis)
        print(f"\n{persona['name']}:")
        print(cevap)
    

    