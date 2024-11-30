import os

from telethon import TelegramClient

# Replace these with your actual API credentials
API_ID = os.getenv("TELEGRAM_API_ID", "your_api_id_here")
API_HASH = os.getenv("TELEGRAM_API_HASH", "your_api_hash_here")

# Create the client and start the session
client = TelegramClient("session_name", API_ID, API_HASH)


async def main():
    print("Logging in...")
    await client.start()
    print("Session created successfully!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
