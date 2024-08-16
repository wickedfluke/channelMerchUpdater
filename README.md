# Telegram Product Availability Bot

This Telegram bot helps admins manage product availability statuses and send automated notifications to specific channels. The bot allows admins to add or remove products, update product statuses, select channels to notify, and manage admin permissions.

## Features

- **Admin Management**: Add or remove admins from the bot.
- **Product Management**: Add products, update their availability status, and remove products.
- **Channel Selection**: Choose channels to which product availability updates will be sent.
- **Automated Notifications**: Schedule product availability updates to be sent to selected channels at specific times.
- **Admin Dashboard**: Admins have a dashboard with options to manage products, channels, and other admins.

## Prerequisites

- Python 3.7+
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
- Your Telegram API ID and hash from [my.telegram.org](https://my.telegram.org)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-repo/telegram-product-bot.git
   cd telegram-product-bot
2. Install the required Python packages:
   ```
    pip install telethon
3. Set up your API credentials:
   
   Open the Python file containing the bot code.
   Replace the api_id, api_hash, and bot_token variables with your own credentials.
## Usage
Start the Bot: 

Run the bot by executing the script in Python:
    
    python bot.py

Set the First Admin: 

After starting the bot, you will be prompted to enter the Telegram ID of the first admin. This admin will have access to all bot features, including adding other admins.

Admin Commands:
/start: Displays the admin dashboard with options to manage products, channels, and other admins.
Admin Functions:
- Add Admin
- Show Admins
- Add Product
- Change Product Status
- Show Channels
- Select Channels
- Show Products
- Set Times

Bot Functions:
   Add Admin: Enter the username of a user to add them as an admin.
   Select Channels: Enter the username or link of the channel to send product availability updates.
   Add Product: Enter the name of the product to add.
   Change Product Status: Update the status of a selected product (Available, Low Stock, Out of Stock).
   Show Admins: List all admins.
   Show Products: Display all products with their current status.
   Show Channels: List all selected channels.
   Set Times: Schedule specific times for automated notifications (in HH
        format).

Automated Notifications:

The bot will automatically send scheduled notifications about product availability to the selected channels at the specified times.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests. If you encounter any bugs or have suggestions for improvements, please open an issue.

This `README.md` provides a clear overview of the bot's functionality, installation steps, and usage instructions. Feel free to customize it as needed!
