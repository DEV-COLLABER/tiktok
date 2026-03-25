import discord
import feedparser
import asyncio
import os

TIKTOK_RSS = os.getenv("TIKTOK_RSS")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1486193867463069777

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.seen = set()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.loop.create_task(self.check_tiktok())

    async def check_tiktok(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            feed = feedparser.parse(TIKTOK_RSS)
            for entry in feed.entries:
                if entry.id not in self.seen:
                    self.seen.add(entry.id)
                    await channel.send(f"🎵 New TikTok just dropped! {entry.link}")
            await asyncio.sleep(300)

bot = MyBot()
bot.run(DISCORD_TOKEN)
