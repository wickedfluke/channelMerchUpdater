from telethon import TelegramClient, events, Button
from telethon.tl.types import PeerChannel
import asyncio
import datetime

api_id = '11978459'
api_hash = '241490569641f4e8818b78526283fae7'
bot_token = '7209764652:AAFd3RiIXul3AAQCvwsYKIMX69ctrbrXGZA'

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

admins = set()  
channels = []  
products = {}  
scheduled_times = []  
first_admin_id = None
user_states = {}  

class ProductStatus:
    DISPONIBILE = "DISPONIBILE🟢"
    IN_ESURIMENTO = "IN ESAURIMENTO🟠"
    ESAURITO = "ESAURITO🔴"

async def set_first_admin():
    global first_admin_id
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
        if event.sender_id == first_admin_id:
            buttons = [
                [Button.inline("Aggiungi Admin", b"add_admin"), Button.inline("Mostra Admin", b"show_admins")],
                [Button.inline("Aggiungi Prodotto", b"add_product"), Button.inline("Cambia Stato Prodotto", b"change_status")],
                [Button.inline("Mostra Canali", b"show_channels"), Button.inline("Seleziona Canali", b"select_channels")],
                [Button.inline("Mostra Prodotti", b"show_products"), Button.inline("Imposta Orari", b"set_times")] 
            ]
        else:
            buttons = [
                [Button.inline("Aggiungi Prodotto", b"add_product"), Button.inline("Cambia Stato Prodotto", b"change_status")],
                [Button.inline("Mostra Canali", b"show_channels"), Button.inline("Seleziona Canali", b"select_channels")],
                [Button.inline("Mostra Prodotti", b"show_products"), Button.inline("Imposta Orari", b"set_times")] 
            ]
        
        await event.respond(
            "Benvenuto! Seleziona un'opzione:",
            buttons=buttons
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
        user_states[event.sender_id] = 'waiting_for_channel_link'
        await event.respond("Invia l'username (es. @username) o il link del canale da aggiungere.")

    elif data == "add_product":
        user_states[event.sender_id] = 'waiting_for_product_name'
        await event.respond("Invia il nome del prodotto da aggiungere.")
    
    elif data == "change_status":
        if products:  
            buttons = [
                [Button.inline(product_name, f"select_product:{product_name}".encode('utf-8'))] 
                for product_name in products.keys()
            ]
            buttons.append([Button.inline("Home", b"home")])
            await event.respond("Seleziona il prodotto:", buttons=buttons)
            user_states[event.sender_id] = 'waiting_for_product_choice'
        else:
            await event.respond(
                "Non ci sono prodotti disponibili.",
                buttons=[Button.inline("Home", b"home")]
            )

    elif data.startswith("select_product:"):
        product_name = data.split(":")[1]
        await event.respond("Seleziona lo stato:",
            buttons=[
                Button.inline(ProductStatus.DISPONIBILE, f"status:{product_name}:{ProductStatus.DISPONIBILE}".encode('utf-8')),
                Button.inline(ProductStatus.IN_ESURIMENTO, f"status:{product_name}:{ProductStatus.IN_ESURIMENTO}".encode('utf-8')),
                Button.inline(ProductStatus.ESAURITO, f"status:{product_name}:{ProductStatus.ESAURITO}".encode('utf-8'))
            ]
        )
        user_states.pop(event.sender_id)
    
    elif data == "show_admins":
        if admins:
            admin_list = "\n".join([f"@{(await client.get_entity(admin_id)).username}" for admin_id in admins if await client.get_entity(admin_id)])
            await event.respond(
                f"Lista degli admin:\n{admin_list}\n\nInvia l'username dell'admin che vuoi rimuovere.",
                buttons=[Button.inline("Home", b"home"), Button.inline("Rimuovi Admin", b"remove_admin")]
            )
        else:
            await event.respond(
                "Non ci sono admin al momento.",
                buttons=[Button.inline("Home", b"home")]
            )

    elif data.startswith("status:"):
        _, product_name, status = data.split(":")
        products[product_name] = status
        await event.respond(
            f"Stato di {product_name} aggiornato a {status}.",
            buttons=[Button.inline("Home", b"home")]
        )
        for channel in channels:
            await client.send_message(channel, f"Il prodotto {product_name} è ora {status}")
    
    elif data == "show_products":
        if products:
            product_list = "\n".join([f"{product}: {status}" for product, status in products.items()])
            await event.respond(
                f"Lista dei prodotti:\n{product_list}",
                buttons=[
                    Button.inline("Home", b"home"),
                    Button.inline("Elimina Prodotto", b"remove_product")
                ]
            )
        else:
            await event.respond(
                "Non ci sono prodotti al momento.",
                buttons=[Button.inline("Home", b"home")]
            )

    elif data == "show_channels":
        if channels:
            channel_list = "\n".join([f"Canale ID: {channel_id}" for channel_id in channels])
            await event.respond(
                f"Lista dei canali:\n{channel_list}",
                buttons=[
                Button.inline("Home", b"home"),
                Button.inline("Rimuovi Canale", b"remove_channel")  
            ]
            )
        else:
            await event.respond(
                "Non ci sono canali selezionati.",
                buttons=[Button.inline("Home", b"home")]
            )

    elif data == "remove_product":
        user_states[event.sender_id] = 'waiting_for_product_removal'
        await event.respond("Invia il nome del prodotto da eliminare.")

    elif data == "remove_channel":
        user_states[event.sender_id] = 'waiting_for_channel_removal'
        await event.respond("Invia l'ID del canale che desideri rimuovere.")

    elif data == "remove_admin":
        user_states[event.sender_id] = 'waiting_for_admin_removal'
        await event.respond("Invia l'username dell'admin che vuoi rimuovere.")

    elif data == "set_times":
        user_states[event.sender_id] = 'waiting_for_times'
        await event.respond("Invia due orari nel formato HH:MM (es. 10:00 18:00).")
    
    elif data == "home":
        await start(event)

@client.on(events.NewMessage)
async def message_handler(event):
    if event.sender_id in user_states:
        state = user_states[event.sender_id]
        
        if state == 'waiting_for_username':
            username = event.message.message.strip()
            try:
                user = await client.get_entity(username)
                admins.add(user.id)
                await event.respond(
                    f"Admin {username} aggiunto con successo.",
                    buttons=[Button.inline("Home", b"home")]
                )
            except Exception as e:
                await event.respond(f"Errore: {e}")
            finally:
                user_states.pop(event.sender_id)

        elif state == 'waiting_for_channel_link':
            channel_link = event.message.message.strip()
            try:
                channel = await client.get_entity(channel_link)
                if 1==1:
                    channels.append(channel.id)
                    await event.respond(
                        f"Canale aggiunto: {channel.title}",
                        buttons=[Button.inline("Home", b"home")]
                    )
                else:
                    await event.respond("Non è un canale valido.", buttons=[Button.inline("Home", b"home")])
            except Exception as e:
                await event.respond(f"Errore: {e}", buttons=[Button.inline("Home", b"home")])
            finally:
                user_states.pop(event.sender_id)

        elif state == 'waiting_for_channel_removal':
            try:
                channel_id = int(event.message.message.strip())
                if channel_id in channels:
                    channels.remove(channel_id)  
                    await event.respond(
                        f"Canale con ID {channel_id} rimosso con successo.",
                        buttons=[Button.inline("Home", b"home")]
                    )
                else:
                    await event.respond(
                        f"Il canale con ID {channel_id} non è nella lista.",
                        buttons=[Button.inline("Home", b"home")]
                    )
            except ValueError:
                await event.respond(
                    "ID del canale non valido. Assicurati di inviare un numero intero.",
                    buttons=[Button.inline("Home", b"home")]
                )
            user_states.pop(event.sender_id)  


        elif state == 'waiting_for_product_removal':
            product_name = event.message.message.strip()
            if product_name in products:
                del products[product_name]  
                await event.respond(
                    f"Prodotto {product_name} eliminato con successo.",
                    buttons=[Button.inline("Home", b"home")]
                )
            else:
                await event.respond(
                    f"Il prodotto {product_name} non esiste.",
                    buttons=[Button.inline("Home", b"home")]
        )
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
                await event.respond(
                    f"Prodotto {product_name} aggiunto con successo.",
                    buttons=[Button.inline("Home", b"home")]
                )
            user_states.pop(event.sender_id)

        elif state == 'waiting_for_times':
            times = event.message.message.strip().split()
            if len(times) == 2:
                scheduled_times.extend(times)
                await event.respond(
                    f"Orari impostati: {', '.join(scheduled_times)}.",
                    buttons=[Button.inline("Home", b"home")]
                )
            else:
                await event.respond("Formato orario non valido. Invia due orari nel formato HH:MM.")
            user_states.pop(event.sender_id)
        
        elif state == 'waiting_for_admin_removal':
            username = event.message.message.strip()
            try:
                user = await client.get_entity(username)
                if user.id in admins:
                    admins.remove(user.id)
                    await event.respond(
                        f"Admin {username} rimosso con successo.",
                        buttons=[Button.inline("Home", b"home")]
                    )
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
    asyncio.create_task(scheduled_message())  

if __name__ == "__main__":
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
