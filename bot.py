from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, RPCError

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import re
import os
from dotenv import load_dotenv
import json
import sys

load_dotenv()
print("API_ID:", os.environ.get("API_ID"))
sys.stdout.flush()

missing_vars = []
if not os.environ.get("API_ID"): missing_vars.append("API_ID")
if not os.environ.get("API_HASH"): missing_vars.append("API_HASH")
if not os.environ.get("GOOGLE_CREDS_JSON"): missing_vars.append("GOOGLE_CREDS_JSON")

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import base64

google_creds_b64 = os.environ.get("GOOGLE_CREDS_B64")
google_creds_json = base64.b64decode(google_creds_b64).decode('utf-8')
google_creds = json.loads(google_creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)

client_gsheet = gspread.authorize(creds)
sheet = client_gsheet.open("LOG").sheet1

client = TelegramClient('forward_bot_session', api_id, api_hash)
TARGET_CHAT_ID = -4689578106
SOURCE_USERNAME = 'mrbob9997'

@client.on(events.NewMessage(incoming=True))
async def forward_message(event):
    try:
        sender = await event.get_sender()
        username = getattr(sender, 'username', None)

        print("\n====================")
        print(f"Raw message: {event.raw_text}")
        sys.stdout.flush()

        if username and username.lower() == SOURCE_USERNAME:
            message = event.message.message
            await client.send_message(TARGET_CHAT_ID, message)
            print("✅ Message forwarded to group")
            sys.stdout.flush()

            amount_match = re.search(r"(\d+(?:\.\d{2})?)", message)
            account_match = re.search(r"account\s+(\d+)", message, re.IGNORECASE)
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            amount = float(amount_match.group(1)) if amount_match else "NOT FOUND"
            account = account_match.group(1) if account_match else "NOT FOUND"

            sheet.append_row([amount, account, date_str, time_str])
            print("\U0001F4DD Logged to Google Sheet")
            sys.stdout.flush()

        else:
            print("⛔ Message ignored (not from target user)")
            sys.stdout.flush()

    except Exception as e:
        print(f"Error: {e}")
        sys.stdout.flush()

if __name__ == '__main__':
    try:
        print("\U0001F680 Bot is running. Waiting for messages...")
        sys.stdout.flush()
        client.start()
        client.run_until_disconnected()
    except SessionPasswordNeededError:
        print("Two-step verification is enabled. Please disable it or handle password login.")
        sys.stdout.flush()
    except RPCError as rpc_err:
        print(f"Telegram RPC error: {rpc_err}")
        sys.stdout.flush()
    except Exception as e:
        print(f"Fatal error: {e.__class__.__name__}: {e}")
        sys.stdout.flush()
