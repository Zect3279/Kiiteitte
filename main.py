import os
from dotenv import load_dotenv
import tweepy
import requests
import datetime
import time
import json

load_dotenv()

NOW_PLAYING_API_URL = "https://cafe.kiite.jp/api/cafe/now_playing"
NOW_PLAYING_API_URL_TOW = "https://cafeapi.kiite.jp/api/cafe/now_playing"

TWEET_FORMAT = """\
♪{} #{} #Kiite
Kiite Cafeできいてます https://cafe.kiite.jp/ https://nico.ms/{}
"""
TWEET_FORMAT_TWO = """\
♪{} （2回目） #{} #Kiite
Kiite Cafeできいてます https://cafe.kiite.jp/ https://nico.ms/{}
"""

DISCORD_HEADER = {'Content-Type': 'application/json'}


# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))
auth.set_access_token(os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))

# Create API object
api = tweepy.API(auth)

def post_tweet(title: str, video_id: str):
  try:
    tweet = TWEET_FORMAT.format(title, video_id, video_id)
    # post tweet
    print(tweet,"\n")
    api.update_status(tweet)
  except:
    tweet2 = TWEET_FORMAT_TWO.format(title, video_id, video_id)
    print(tweet2,"\n")
    api.update_status(tweet2)

def post_discord(data):
  title = data["title"]
  video_id = data["video_id"]
  view = data["baseinfo"]["view_counter"]
  comment = data["baseinfo"]["comment_num"]
  mylist = data["baseinfo"]["mylist_counter"]
  author_name = data["baseinfo"]["user_nickname"]
  author_icon = data["baseinfo"]["user_icon_url"]
  timestamp = data["start_time"]
  video_img = data["baseinfo"]["thumbnail_url"]
  # print(title, video_id, view, comment, mylist, author_name, author_icon, timestamp, video_img)
  discord = {"username": "Kiiteitte","avatar_url": "https://pbs.twimg.com/profile_images/1584526973505634304/M686vgg3_400x400.jpg","content": None}
  discord.update({"embeds":[{"title": f"♪ {title}","url": f"https://nico.ms/{video_id}","fields": [{"name": "▶ 再生数","value": f"{view}","inline": True},{"name": "📔 コメント数","value": f"{comment}","inline": True},{"name": "🖊️ マイリス数","value": f"{mylist}","inline": True}],"author": {"name": f"{author_name}","icon_url": f"{author_icon}"},"timestamp": f"{timestamp}","thumbnail": {"url": f"{video_img}"}}]})
  requests.post(os.getenv('WEBHOOK_URL'), json.dumps(discord), headers=DISCORD_HEADER)

while True:
  row_data = {}
  data = {}
  duration = 0
  try:
    row_data = requests.get(NOW_PLAYING_API_URL)
    data = row_data.json()
    duration = data['msec_duration']
  except:
    print('2')
    row_data = requests.get(NOW_PLAYING_API_URL_TOW)
    data = row_data.json()
    duration = data['msec_duration']
  start_time = datetime.datetime.fromisoformat(data['start_time'])
  timezone = datetime.timezone(datetime.timedelta(hours=9))
  now_time = datetime.datetime.now(timezone)
  wait_time = (start_time - now_time).total_seconds() + (duration/1000) + 2
  post_discord(data)
  post_tweet(data['title'], data['video_id'])
  time.sleep(wait_time)

