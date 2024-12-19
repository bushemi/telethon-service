import asyncio
import logging
import os
from datetime import datetime

from flask import Flask, request, jsonify
from telethon import TelegramClient

# Load API credentials from environment variables
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    raise ValueError(
        "API_ID or API_HASH is not set. Please check your .env file.")

# Create the Telegram client using the pre-existing session file
client = TelegramClient("session_name", API_ID, API_HASH)

# Initialize Flask app
app = Flask(__name__)

# Global event loop for managing asyncio
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)

# Configure logging to show logs on console
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


# Function to run async code in a separate thread
def run_async_func(func, *args):
    return loop.run_until_complete(func(*args))


@app.route("/chat/<string:chat_id>/getMessages", methods=["GET"])
def get_messages(chat_id):
    try:
        # Convert chat_id to integer
        chat_id = int(chat_id)

        # Get 'limit' and 'from' parameters from the query string
        limit = int(
            request.args.get("limit", 5))  # Default to 5 if not provided
        from_id = int(
            request.args.get("from", 0))  # Default to 0 if not provided

        # Run the async function in a separate thread to avoid blocking Flask
        messages = run_async_func(fetch_messages, chat_id, limit, from_id)
        messages_total = run_async_func(get_total_messages, chat_id)

        # Format the messages in a simple structure
        message_list = [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "message": msg.text,
                "date": str(msg.date),
                "whole_msg": str(msg)
            }
            for msg in messages
        ]

        # Return JSON response with the fetched messages and parameters used
        response = {
            "messages": message_list,
            "chatId": chat_id,
            "limit": limit,
            "from": from_id,
            "total": messages_total
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


async def get_total_messages(chat_id):
    """Fetch the total number of messages in a chat."""
    try:
        # Use limit=0 to only fetch metadata, including the total count
        messages = await client.get_messages(chat_id, limit=0)
        return messages.total
    except Exception as e:
        raise RuntimeError(f"Failed to fetch total message count: {str(e)}")


@app.route("/chats/total", methods=["GET"])
def get_total_chat_count():
    try:
        total_chats = run_async_func(get_total_chats)
        return jsonify({"total_chats": total_chats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


async def get_total_chats():
    # """Fetch the total number of chats (dialogs)."""
    try:
        # Fetch dialogs with limit=0 to get only the count
        dialogs = await client.get_dialogs(limit=0)
        return dialogs.total
    except Exception as e:
        return {"error": str(e)}


@app.route("/get_messages", methods=["POST"])
def get_first_messages():
    try:
        # Get the number of messages from the request
        data = request.json
        num_messages = int(
            data.get("num_messages", 20))  # Default to 20 messages

        # Run the asynchronous fetch_messages function using the existing loop
        result = run_async_func(fetch_first_messages, num_messages)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_chats", methods=["GET"])
def get_chats():
    try:
        # Get the 'limit' and 'from' parameters from the query string
        limit = int(
            request.args.get("limit", 10))  # Default to 5 if not provided
        offset_id = int(
            request.args.get("offset_id", 0))  # Default to 0 if not provided
        offset_date = request.args.get(
            "offset_date", None)
        # Default to None if not provided
        print("offset_date ", offset_date)
        if offset_date:
            offset_date = datetime.fromisoformat(offset_date)
        ignore_pinned = request.args.get(
            "ignore_pinned", False)  # Default to False if not provided
        ignore_migrated = request.args.get(
            "ignore_migrated", False)  # Default to False if not provided
        folder = request.args.get(
            "folder", None)  # Default to None if not provided
        archived = request.args.get(
            "archived", None)  # Default to None if not provided
        # Get the 'filter' parameter from the query string (default to None if not provided)
        chat_filter = request.args.get("filter",
                                       None)  # Filter can be 'group', 'channel', or None

        # Run the asynchronous fetch_chats function with the parameters
        chats = run_async_func(fetch_chats, limit, offset_id, chat_filter,
                               offset_date, ignore_pinned, ignore_migrated,
                               folder, archived)
        return jsonify(chats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


async def fetch_first_messages(num_messages):
    await client.start()
    dialogs = await client.get_dialogs(limit=1)
    if not dialogs:
        return {"error": "No chats found!"}

    first_chat = dialogs[0]
    messages = await client.get_messages(first_chat, limit=num_messages)
    return [
        {
            "date": str(message.date),
            "sender_id": message.sender_id,
            "text": message.text or "",
        }
        for message in messages
    ]


# Function to fetch messages from a chat
async def fetch_messages(chat_id, limit=5, from_id=0):
    await client.start()  # Start the client if not already started

    # Get messages from the specified chat ID
    # The chat_id can be a user ID, group ID, or channel ID
    try:
        messages = await client.get_messages(chat_id, limit=limit,
                                             offset_id=from_id)
        return messages
    except Exception as e:
        return {"error": str(e)}


async def fetch_chats(limit,
                      offset_id,
                      chat_filter,
                      offset_date,
                      ignore_pinned,
                      ignore_migrated,
                      folder,
                      archived):
    await client.start()
    dialogs = await client.get_dialogs(
        limit=limit,
        offset_date=offset_date,
        offset_id=offset_id,
        ignore_pinned=ignore_pinned,
        ignore_migrated=ignore_migrated,
        folder=folder,
        archived=archived)  # Fetch the limited number of dialogs
    # https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.dialogs.DialogMethods.get_dialogs

    # Filter the dialogs based on the 'filter' parameter (if provided)
    if chat_filter:
        if chat_filter == "group":
            dialogs = [dialog for dialog in dialogs if dialog.is_group]
        elif chat_filter == "channel":
            dialogs = [dialog for dialog in dialogs if dialog.is_channel]

    chat_list = [
        {
            "id": dialog.id,
            "name": dialog.name,
            "is_group": dialog.is_group,
            "is_channel": dialog.is_channel,
            "date": str(dialog.date),
            # Convert to string for JSON serialization
            "whole_dialog": str(dialog),
        }
        for dialog in dialogs
    ]
    return chat_list


if __name__ == "__main__":
    # Connect Telethon client once at the start
    run_async_func(client.connect)
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        # Disconnect Telethon client gracefully when the app shuts down
        run_async_func(client.disconnect)
