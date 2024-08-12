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

user_states = {}  # Dizionario per memorizzare lo stato dell'utente

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
                [Button.inline("Imposta Orari", b"set_times"), Button.inline("Mostra Admin", b"show_admins")]
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
        user_states[event.sender_id] = 'waiting_for_username'
        await event.respond("Invia il nome utente (es. @username) da aggiungere come admin.")
    
    elif data == "select_channels":
        if event.sender_id in user_states and user_states[event.sender_id] == 'waiting_for_username':
            user_states.pop(event.sender_id)
            async for dialog in client.iter_dialogs():
                if isinstance(dialog.entity, PeerChannel):
                    channels.append(dialog.entity.id)
                    await event.respond(f"Canale aggiunto: {dialog.title}")

    elif data == "add_product":
        user_states[event.sender_id] = 'waiting_for_product_name'
        await event.respond("Invia il nome del prodotto da aggiungere.")
    
    elif data == "change_status":
        user_states[event.sender_id] = 'waiting_for_product_name'
        await event.respond("Seleziona il prodotto:")
    
    elif data == "show_admins":
        if admins:
            admin_list = "\n".join([f"@{(await client.get_entity(admin_id)).username}" for admin_id in admins if await client.get_entity(admin_id)])
            await event.respond(f"Lista degli admin:\n{admin_list}\n\nInvia l'username dell'admin che vuoi rimuovere.")
            user_states[event.sender_id] = 'waiting_for_admin_removal'
        else:
            await event.respond("Non ci sono admin al momento.")

    elif data.startswith("status:"):
        _, product_name, status = data.split(":")
        products[product_name] = status
        await event.respond(f"Stato di {product_name} aggiornato a {status}.")
        for channel in channels:
            await client.send_message(channel, f"Il prodotto {product_name} è ora {status}.")
    
    elif data == "set_times":
        user_states[event.sender_id] = 'waiting_for_times'
        await event.respond("Invia due orari nel formato HH:MM (es. 10:00 18:00).")

@client.on(events.NewMessage)
async def message_handler(event):
    if event.sender_id in user_states:
        state = user_states[event.sender_id]
        
        if state == 'waiting_for_username':
            username = event.message.message.strip()
            try:
                user = await client.get_entity(username)
                admins.add(user.id)
                await event.respond(f"Admin {username} aggiunto con successo.")
            except Exception as e:
                await event.respond(f"Errore: {e}")
            finally:
                user_states.pop(event.sender_id)

        elif state == 'waiting_for_product_name':
            product_name = event.message.message.strip()
            if product_name in products:
                await event.respond("Seleziona lo stato:",
                    buttons=[
                        Button.inline(ProductStatus.DISPONIBILE, f"status:{product_name}:{ProductStatus.DISPONIBILE}".encode('utf-8')),
                        Button.inline(ProductStatus.IN_ESURIMENTO, f"status:{product_name}:{ProductStatus.IN_ESURIMENTO}".encode('utf-8')),
                        Button.inline(ProductStatus.ESAURITO, f"status:{product_name}:{ProductStatus.ESAURITO}".encode('utf-8'))
                    ]
                )
            else:
                products[product_name] = ProductStatus.DISPONIBILE
                await event.respond(f"Prodotto {product_name} aggiunto con successo.")
            user_states.pop(event.sender_id)
        
        elif state == 'waiting_for_times':
            times = event.message.message.strip().split()
            if len(times) == 2:
                scheduled_times.extend(times)
                await event.respond(f"Orari impostati: {', '.join(scheduled_times)}.")
            else:
                await event.respond("Formato orario non valido. Invia due orari nel formato HH:MM.")
            user_states.pop(event.sender_id)
        
        elif state == 'waiting_for_admin_removal':
            username = event.message.message.strip()
            try:
                user = await client.get_entity(username)
                if user.id in admins:
                    admins.remove(user.id)
                    await event.respond(f"Admin {username} rimosso con successo.")
                else:
                    await event.respond("Questo utente non è un admin.")
            except Exception as e:
                await event.respond(f"Errore: {e}")
            finally:
                user_states.pop(event.sender_id)

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
    asyncio.create_task(scheduled_message())  # Avvia il task per i messaggi programmati

if __name__ == "__main__":
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
