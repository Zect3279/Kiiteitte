import os
from dotenv import load_dotenv
import tweepy
import requests
import datetime
import time

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

# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))
auth.set_access_token(os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))

# Create API object
api = tweepy.API(auth)

def post_tweet(title: str, video_id: str):
  try:
    tweet = TWEET_FORMAT.format(title, video_id, video_id)
    # post tweet
    print(tweet)
    api.update_status(tweet)
  except:
    tweet2 = TWEET_FORMAT_TWO.format(title, video_id, video_id)
    print(tweet2)
    api.update_status(tweet2)


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
  post_tweet(data['title'], data['video_id'])
  time.sleep(wait_time)

