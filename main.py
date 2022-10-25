import os
from dotenv import load_dotenv
import tweepy
from warnings import catch_warnings
import requests
import datetime
import time

load_dotenv()

NOW_PLAYING_API_URL = "https://cafeapi.kiite.jp/api/cafe/now_playing"
TWEET_FORMAT = """\
♪{} #{} #Kiite
Kiite Cafeできいてます https://cafe.kiite.jp/ https://nico.ms/{}
"""

# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))
auth.set_access_token(os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))

# Create API object
api = tweepy.API(auth)

def post_tweet(title: str, video_id: str):
  tweet = TWEET_FORMAT.format(title, video_id, video_id)
  # post tweet
  print(tweet)
  api.update_status(tweet)

while True:
  data = requests.get(NOW_PLAYING_API_URL).json()
  duration = data['msec_duration']
  start_time = datetime.datetime.fromisoformat(data['start_time'])
  timezone = datetime.timezone(datetime.timedelta(hours=9))
  now_time = datetime.datetime.now(timezone)
  wait_time = (start_time - now_time).total_seconds() + (duration/1000) + 1
  post_tweet(data['title'], data['video_id'])
  time.sleep(wait_time)

