import discord
import asyncio
import os
from TikTokApi import TikTokApi

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TIKTOK_USERS = os.getenv("TIKTOK_USERNAMES").split(",")
CHANNEL_ID = 1486193867463069777

USER_NAMES = {
    TIKTOK_USERS[0]: "Binwalk",
    TIKTOK_USERS[1]: "Anas",
}

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
        async with TikTokApi() as api:
            await api.create_sessions(num_sessions=1, sleep_after=3, headless=True)
            while not self.is_closed():
                for username in TIKTOK_USERS:
                    try:
                        user = api.user(username)
                        videos = []
                        async for video in user.videos(count=1):
                            videos.append(video)
                        if videos:
                            latest_id = videos[0].id
                            if latest_id != self.last_video.get(username):
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
