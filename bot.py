import discord
import asyncio
import os
import requests
import xml.etree.ElementTree as ET
import json

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TIKTOK_USERS = os.getenv("TIKTOK_USERNAMES").split(",")
CHANNEL_ID = 1486193867463069777

USER_NAMES = {
    TIKTOK_USERS[0]: "Binwalk",
    TIKTOK_USERS[1]: "Anas",
}

def get_latest_video(username):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    }
    url = f"https://www.tiktok.com/api/user/detail/?uniqueId={username}&aid=1988"
    r = requests.get(url, headers=headers)
    print(f"Status for {username}: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    data = r.json()
    user_id = data["userInfo"]["user"]["id"]
    
    feed_url = f"https://www.tiktok.com/api/post/item_list/?aid=1988&userId={user_id}&count=1"
    r2 = requests.get(feed_url, headers=headers)
    print(f"Feed status: {r2.status_code}")
    print(f"Feed response: {r2.text[:500]}")
    items = r2.json().get("itemList", [])
    if items:
        return items[0]["id"]
    return None

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.last_video = {}

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.loop.create_task(self.check_tiktok())

    async def check_tiktok(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            for username in TIKTOK_USERS:
                try:
                    latest_id = get_latest_video(username)
                    print(f"{username} latest video: {latest_id}")
                    if latest_id and latest_id != self.last_video.get(username):
                        if username in self.last_video:
                            display = USER_NAMES.get(username, username)
                            url = f"https://www.tiktok.com/@{username}/video/{latest_id}"
                            await channel.send(f"@everyone {display} just posted a new video, go check it out!! {url}")
                        self.last_video[username] = latest_id
                except Exception as e:
                    print(f"Error checking {username}: {e}")
            await asyncio.sleep(300)

bot = MyBot()
bot.run(DISCORD_TOKEN)
