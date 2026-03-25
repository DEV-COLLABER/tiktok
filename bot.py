import discord
import asyncio
import os
import requests
import xml.etree.ElementTree as ET

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TIKTOK_USERS = os.getenv("TIKTOK_USERNAMES").split(",")
CHANNEL_ID = 1486193867463069777

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
                    url = f"https://www.tiktok.com/@{username}/rss"
                    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    if r.status_code == 200:
                        root = ET.fromstring(r.content)
                        items = root.findall("./channel/item")
                        if items:
                            latest = items[0].find("link").text
                            if latest != self.last_video.get(username):
                                if username in self.last_video:
                                    await channel.send(f"🎵 **@{username}** just posted a new TikTok! {latest}")
                                self.last_video[username] = latest
                except Exception as e:
                    print(f"Error checking {username}: {e}")
            await asyncio.sleep(300)

bot = MyBot()
bot.run(DISCORD_TOKEN)
