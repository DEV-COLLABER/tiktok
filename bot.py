import discord
import asyncio
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME")
CHANNEL_ID = 1486193867463069777

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.last_video_id = None

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.loop.create_task(self.check_tiktok())

    async def check_tiktok(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            try:
                url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/rss"
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(r.content)
                    items = root.findall("./channel/item")
                    if items:
                        latest = items[0]
                        video_id = latest.find("link").text
                        if video_id != self.last_video_id:
                            if self.last_video_id is not None:
                                await channel.send(f"🎵 New TikTok just dropped! {video_id}")
                            self.last_video_id = video_id
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(300)

bot = MyBot()
bot.run(DISCORD_TOKEN)
