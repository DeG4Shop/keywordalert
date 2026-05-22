import json
import os
from telethon import TelegramClient, events

API_ID   = 38658405 # sostituisci con il tuo api_id
API_HASH = "d3324cbb1a5a049f5d876b213d77ceac"  # sostituisci con il tuo api_hash
KEYWORDS_FILE = "keywords.json"

def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE) as f:
            return json.load(f)
    return []

def save_keywords(kws):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(kws, f)

keywords = load_keywords()

client = TelegramClient("sessione_alert", API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r"/add (.+)", outgoing=True))
async def add_keyword(event):
    kw = event.pattern_match.group(1).strip().lower()
    if kw not in keywords:
        keywords.append(kw)
        save_keywords(keywords)
        await event.edit(f"✅ Keyword aggiunta: {kw}")
    else:
        await event.edit(f"⚠️ '{kw}' è già nella lista")

@client.on(events.NewMessage(pattern=r"/remove (.+)", outgoing=True))
async def remove_keyword(event):
    kw = event.pattern_match.group(1).strip().lower()
    if kw in keywords:
        keywords.remove(kw)
        save_keywords(keywords)
        await event.edit(f"🗑️ Keyword rimossa: {kw}")
    else:
        await event.edit(f"❌ '{kw}' non trovata")

@client.on(events.NewMessage(pattern=r"/list", outgoing=True))
async def list_keywords(event):
    if keywords:
        lista = "\n".join(f"• {k}" for k in keywords)
        await event.edit(f"🔍 Keywords attive:\n{lista}")
    else:
        await event.edit("📭 Nessuna keyword impostata")

@client.on(events.NewMessage(incoming=True))
async def monitor(event):
    if not keywords:
        return
    if not (event.is_group or event.is_channel):
        return
    testo = (event.text or "").lower()
    for kw in keywords:
        if kw in testo:
            chat = await event.get_chat()
            nome_chat = getattr(chat, "title", "Chat sconosciuta")
            await client.send_message("me",
                f"🔔 Keyword trovata: {kw}\n\n"
                f"📌 Gruppo/Canale: {nome_chat}\n"
                f"👤 Da: {getattr(event.sender, 'first_name', 'Sconosciuto')}\n\n"
                f"💬 {event.text[:300]}"
            )
            break

print("🤖 Keyword Alert attivo!")
with client:
    client.run_until_disconnected()