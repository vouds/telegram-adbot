from telethon import TelegramClient, errors
import asyncio
import requests
import re

#by @voudx on tele
# free tool do whatever with it idk its kinda lame if u resell though

#telegram acc creds - get them at https://my.telegram.org/

api_id_1 = 123456789
api_hash_1 = 'ahhh hash'
session_name_1 = 'account1'

api_id_2 = 987654321
api_hash_2 = 'ahhh hash'
session_name_2 = 'account2'

# conf
message_link = "put ur message to forward here"

target_channels = [
    "t.me/channel1",
    "t.me/channel2",
    "t.me/channel3",
    "t.me/channel4",
    "t.me/channel5",
    't.me/channel6',
    "t.me/channel7",
    "t.me/channel8"
]

webhook_url = "discord webhook for pass/fail rate"

delay_between_forwards = 5  #delay btwn forwards
delay_between_cycles = 300   #delay for full cycle

special_message = "this one is for a specific channel that you want to post in but for example they dont allow links or whatever"  #specified channel on line 85

# ─────────────────────────────────────────────────────────────

async def get_message_from_url(client, url):
    match = re.match(r'https://t\.me/([\w\d_]+)/(\d+)', url)
    if not match:
        raise ValueError("Invalid message URL format")
    username = match.group(1)
    msg_id = int(match.group(2))
    entity = await client.get_entity(username)
    msg = await client.get_messages(entity, ids=msg_id)
    return msg

def send_webhook_log(account, results):
    embed = {
        "title": f"Forward Results - {account}",
        "color": 0x2ecc71 if all(r['success'] for r in results) else 0xe74c3c,
        "fields": []
    }
    for r in results:
        embed["fields"].append({
            "name": r["channel"],
            "value": "✅ Success" if r["success"] else f"❌ Failed\n`{r['error']}`",
            "inline": False
        })
    data = {"embeds": [embed]}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code not in (200, 204):
            print(f"[Webhook Error] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Webhook Exception] {e}")

async def forward_from_account(client, account_name, assigned_channels):
    print(f"[{account_name}] Resolving message link...")
    results = []
    try:
        msg = await get_message_from_url(client, message_link)
    except Exception as e:
        print(f"[{account_name}] Error fetching message: {e}")
        return
    for channel in assigned_channels:
        try:
            channel_id = channel
            if channel.startswith("https://t.me/") or channel.startswith("t.me/"):
                channel_id = channel.split("t.me/")[1].strip("/")
            if channel_id == "THIS IS THE SPECIAL CHANNEL":
                await client.send_message(channel_id, special_message)
                print(f"[{account_name}] ✅ Sent special message to {channel_id}")
                results.append({"channel": channel_id, "success": True})
                await asyncio.sleep(delay_between_forwards)
                continue
            try:
                await client.forward_messages(channel_id, msg)
                print(f"[{account_name}] ✅ Forwarded to {channel_id}")
                results.append({"channel": channel_id, "success": True})
            except Exception as forward_err:
                print(f"[{account_name}] ❌ Forward failed to {channel_id}: {forward_err}, sending special message instead.")
                await client.send_message(channel_id, special_message)
                results.append({"channel": channel_id, "success": True, "note": "Forward failed, sent special message instead."})
            await asyncio.sleep(delay_between_forwards)
        except Exception as e:
            print(f"[{account_name}] ❌ Failed to process {channel}: {e}")
            results.append({"channel": channel, "success": False, "error": str(e)})

    send_webhook_log(account_name, results)

async def main():
    client1 = TelegramClient(session_name_1, api_id_1, api_hash_1)
    client2 = TelegramClient(session_name_2, api_id_2, api_hash_2)

    await client1.start()
    await client2.start()

    print("[Main] Logged into both accounts.")

    client1_channels = target_channels[::2]
    client2_channels = target_channels[1::2]

    while True:
        print("\n[Main] Starting new forward cycle...")
        await asyncio.gather(
            forward_from_account(client1, "Account 1", client1_channels),
            forward_from_account(client2, "Account 2", client2_channels)
        )
        print(f"[Main] Cycle complete. Waiting {delay_between_cycles} seconds...\n")
        await asyncio.sleep(delay_between_cycles)

asyncio.run(main())
