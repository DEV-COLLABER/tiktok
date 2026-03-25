import discord                              
  import asyncio                                                          
  import os                                                               
  import requests   
  import json                                                             
                                                            
  DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")                              
  TIKTOK_USERS = os.getenv("TIKTOK_USERNAMES").split(",")
  CHANNEL_ID = int(os.getenv("CHANNEL_ID", "1486193867463069777"))
  STATE_FILE = "last_videos.json"

  USER_NAMES = {
      "dev-collab": "Binwalk",
      "dev-collab-2": "Anas",
  }

  def load_state():
      """Load last seen video IDs from file"""
      if os.path.exists(STATE_FILE):
          try:
              with open(STATE_FILE, "r") as f:
                  return json.load(f)
          except Exception as e:
              print(f"Error loading state: {e}")
      return {}

  def save_state(state):
      """Save last seen video IDs to file"""
      try:
          with open(STATE_FILE, "w") as f:
              json.dump(state, f)
      except Exception as e:
          print(f"Error saving state: {e}")

  def get_latest_video(username):
      """Fetch latest video ID from TikTok using unofficial API"""
      headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)
  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
          "Referer": "https://www.tiktok.com/",
          "Accept": "application/json, text/plain, */*",
      }

      # Try using TikTok's oembed endpoint first (more reliable)
      embed_url =
  f"https://www.tiktok.com/oembed?url=https://www.tiktok.com/@{username}"
      try:
          r = requests.get(embed_url, headers=headers, timeout=10)
          print(f"Embed status for {username}: {r.status_code}")
          if r.status_code == 200:
              data = r.json()
              # Extract video URL from embed HTML and get video ID
              html = data.get("html", "")
              if 'data-video-id="' in html:
                  import re
                  match = re.search(r'data-video-id="(\d+)"', html)
                  if match:
                      return match.group(1)
      except Exception as e:
          print(f"Embed failed for {username}: {e}")

      # Fallback: Try web scraping approach
      try:
          url = f"https://www.tiktok.com/@{username}"
          r = requests.get(url, headers=headers, timeout=10)
          print(f"Profile status for {username}: {r.status_code}")

          if r.status_code == 200:
              # Look for video IDs in the HTML
              import re
              # TikTok embeds video IDs in the page
              matches = re.findall(r'"id":"(\d{19})"', r.text)
              if matches:
                  return matches[0]
      except Exception as e:
          print(f"Profile scrape failed for {username}: {e}")

      return None

  class MyBot(discord.Client):
      def __init__(self):
          super().__init__(intents=discord.Intents.default())
          # Load state from file so we persist across GitHub Actions runs
          self.last_video = load_state()
          print(f"Loaded state: {self.last_video}")

      async def on_ready(self):
          print(f"Logged in as {self.user}")
          self.loop.create_task(self.check_tiktok())

      async def check_tiktok(self):
          await self.wait_until_ready()
          channel = self.get_channel(CHANNEL_ID)

          if channel is None:
              print(f"ERROR: Could not find channel {CHANNEL_ID}")
              print("Available channels:", list(self.get_all_channels()))
              await self.close()
              return

          print(f"Checking TikTok for users: {TIKTOK_USERS}")

          for username in TIKTOK_USERS:
              username = username.strip().lower()
              try:
                  latest_id = get_latest_video(username)
                  print(f"{username} latest video: {latest_id}")

                  if latest_id is None:
                      print(f"Could not fetch video for {username},
  skipping...")
                      continue

                  previous_id = self.last_video.get(username)
                  print(f"{username}: previous={previous_id},
  current={latest_id}")

                  if latest_id != previous_id:
                      if previous_id is not None:
                          # This is a NEW video (not the first time we've
  seen this user)
                          display = USER_NAMES.get(username, username)
                          url =
  f"https://www.tiktok.com/@{username}/video/{latest_id}"
                          message = f"@everyone {display} just posted a
  new video, go check it out!! {url}"
                          print(f"Sending notification: {message}")
                          try:
                              await channel.send(message)
                              print(f"Notification sent successfully!")
                          except Exception as e:
                              print(f"Failed to send Discord message:
  {e}")
                      else:
                          print(f"First time seeing {username}, storing
  video ID without notification")

                      # Update and save state
                      self.last_video[username] = latest_id
                      save_state(self.last_video)
                  else:
                      print(f"No new videos for {username}")

              except Exception as e:
                  print(f"Error checking {username}: {e}")
                  import traceback
                  traceback.print_exc()

          # Close bot after checking (for GitHub Actions)
          print("Done checking, shutting down...")
          await self.close()

  bot = MyBot()
  bot.run(DISCORD_TOKEN)

