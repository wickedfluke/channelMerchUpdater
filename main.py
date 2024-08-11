from telethon import TelegramClient, events, Button
from telethon.tl.types import PeerChannel
import asyncio
import datetime

api_id = '11978459'
api_hash = '241490569641f4e8818b78526283fae7'
bot_token = '7209764652:AAFd3RiIXul3AAQCvwsYKIMX69ctrbrXGZA'

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

admins = set()  # Insieme per mantenere la lista degli admin
channels = []  # Lista di canali dove inviare messaggi
products = {}  # Dizionario di prodotti con stati
scheduled_times = []  # Lista degli orari fissi

class ProductStatus:
    DISPONIBILE = "Disponibile"
    IN_ESURIMENTO = "In esaurimento"
    ESAURITO = "Esaurito"

async def set_first_admin():
    while True:
        try:
            first_admin_id = int(input("Inserisci l'ID Telegram del primo admin: "))
            admins.add(first_admin_id)
            print(f"Admin {first_admin_id} aggiunto con successo!")
            break
        except ValueError:
            print("Per favore inserisci un ID valido.")

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id in admins:
        await event.respond(
            "Benvenuto! Seleziona un'opzione:",
            buttons=[
                [Button.inline("Aggiungi Admin", b"add_admin"), Button.inline("Seleziona Canali", b"select_channels")],
                [Button.inline("Aggiungi Prodotto", b"add_product"), Button.inline("Cambia Stato Prodotto", b"change_status")],
                [Button.inline("Imposta Orari", b"set_times")]
            ]
        )
    else:
        await event.respond("Benvenuto! Contatta l'amministratore per essere aggiunto.")

@client.on(events.CallbackQuery)
async def callback_handler(event):
    if event.sender_id not in admins:
        await event.answer("Non hai i permessi per eseguire questa azione.", alert=True)
        return
    
    data = event.data.decode('utf-8')
    
    if data == "add_admin":
        await event.respond("Invia il nome utente (es. @username) da aggiungere come admin.")
        response = await client.get_response(event.chat_id, timeout=30)
        new_admin_username = response.message
        admins.add(new_admin_username)
        await event.respond(f"Admin {new_admin_username} aggiunto con successo.")

    elif data == "select_channels":
        async for dialog in client.iter_dialogs():
            if isinstance(dialog.entity, PeerChannel):
                channels.append(dialog.entity.id)
                await event.respond(f"Canale aggiunto: {dialog.title}")
    
    elif data == "add_product":
        await event.respond("Invia il nome del prodotto da aggiungere.")
        response = await client.get_response(event.chat_id, timeout=30)
        product_name = response.message
        products[product_name] = ProductStatus.DISPONIBILE
        await event.respond(f"Prodotto {product_name} aggiunto con successo.")
    
    elif data == "change_status":
        await event.respond("Seleziona il prodotto:")
        response = await client.get_response(event.chat_id, timeout=30)
        product_name = response.message

        if product_name in products:
            await event.respond(
                "Seleziona lo stato:",
                buttons=[
                    Button.inline(ProductStatus.DISPONIBILE, f"status:{product_name}:{ProductStatus.DISPONIBILE}".encode('utf-8')),
                    Button.inline(ProductStatus.IN_ESURIMENTO, f"status:{product_name}:{ProductStatus.IN_ESURIMENTO}".encode('utf-8')),
                    Button.inline(ProductStatus.ESAURITO, f"status:{product_name}:{ProductStatus.ESAURITO}".encode('utf-8'))
                ]
            )
        else:
            await event.respond("Prodotto non trovato.")
    
    elif data.startswith("status:"):
        _, product_name, status = data.split(":")
        products[product_name] = status
        await event.respond(f"Stato di {product_name} aggiornato a {status}.")
        for channel in channels:
            await client.send_message(channel, f"Il prodotto {product_name} è ora {status}.")
    
    elif data == "set_times":
        await event.respond("Invia due orari nel formato HH:MM (es. 10:00 18:00).")
        response = await client.get_response(event.chat_id, timeout=30)
        times = response.message.split()
        scheduled_times.extend(times)
        await event.respond(f"Orari impostati: {', '.join(scheduled_times)}.")

async def scheduled_message():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now in scheduled_times:
            message = "Disponibilità dei prodotti:\n"
            for product, status in products.items():
                message += f"{product}: {status}\n"
            for channel in channels:
                await client.send_message(channel, message)
        await asyncio.sleep(60)

async def main():
    await set_first_admin()
    await client.start()
    await scheduled_message()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
