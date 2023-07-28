

import os
from dotenv import load_dotenv
import requests
import datetime
import time
import json

load_dotenv()

NOW_PLAYING_API_URL = "https://cafe.kiite.jp/api/cafe/now_playing"
NOW_PLAYING_API_URL_TWO = "https://cafeapi.kiite.jp/api/cafe/now_playing"

TWEET_FORMAT = """\
♪{} #{} #Kiite
Kiite Cafeできいてます https://cafe.kiite.jp/ https://nico.ms/{}
"""
TWEET_FORMAT_TWO = """\
♪{} （2回目） #{} #Kiite
Kiite Cafeできいてます https://cafe.kiite.jp/ https://nico.ms/{}
"""

DISCORD_HEADER = {'Content-Type': 'application/json'}

def check_stage(data):
  np_id = data["id"]
  title = data["title"]
  video_id = data["video_id"]
  timestamp = data["start_time"]
  np_reasons = data["reasons"]
  video_img = data["baseinfo"]["thumbnail_url"]

  uj = json.loads(requests.get("https://cafeapi.kiite.jp/api/cafe/users?limit=300").text)
  comments = json.loads(requests.get("https://cafeapi.kiite.jp/api/cafe/user_comments").text)
  new_fav = json.loads(requests.get(f"https://cafeapi.kiite.jp/api/cafe/new_fav?id={np_id}").text)
  rotates = json.loads(requests.get(f"https://cafeapi.kiite.jp/api/cafe/user_gestures?id={np_id}").text)
  fav_reason = [item["user_id"] for item in np_reasons if item["type"] == "favorite"]

  now = str(datetime.datetime.now())

  gas = {
  "id": np_id,
  "user_count": len(uj),
  "rotate_count": len(rotates),
  "new_fav_count": len(new_fav),
  "fav_count": len(new_fav)+len(fav_reason)
  }
  discord = {
    "username": "Kiiteitte",
    "avatar_url":
    "https://pbs.twimg.com/profile_images/1584526973505634304/M686vgg3_400x400.jpg",
    "content": None
  }
  discord.update({
    "embeds": [
    {
      "title": timestamp,
      "description": f"[♪ {title}](https://nico.ms/{video_id})",
      "color": None,
      "footer": {
        "text": f"回: {len(rotates)} / ♡: {len(new_fav)+len(fav_reason)}(+ {len(new_fav)})"
      },
      "thumbnail": {
        "url": f"{video_img}"
      }
    }]
  })
  requests.post(os.getenv('WEBHOOK_URL'), json.dumps(discord), headers=DISCORD_HEADER)
      # requests.post(os.getenv('SP_SH'), data=json.dumps(gas))
      # print(now)
  pass

def post_discord(data):
  np_id = data["id"]
  title = data["title"]
  video_id = data["video_id"]
  view = data["baseinfo"]["view_counter"]
  comment = data["baseinfo"]["comment_num"]
  mylist = data["baseinfo"]["mylist_counter"]
  timestamp = data["start_time"]
  video_img = data["baseinfo"]["thumbnail_url"]
  reasons = data["reasons"]
  try:
    author_name = data["baseinfo"]["user_nickname"]
    author_icon = data["baseinfo"]["user_icon_url"]
  except:
    author_name = "N/A"
    author_icon = ""

  start_time = datetime.datetime.fromisoformat(data["start_time"])
  end_time = start_time + datetime.timedelta(milliseconds=data["msec_duration"])
  end_time_str = end_time.isoformat()

  print(title, video_id, view, comment, mylist, author_name, author_icon,
        timestamp, video_img, '\n')
  discord = {
    "username": "Kiiteitte",
    "avatar_url":
    "https://pbs.twimg.com/profile_images/1584526973505634304/M686vgg3_400x400.jpg",
    "content": None
  }
  discord.update({
    "embeds": [{
      "title":
      f"♪ {title}",
      "url":
      f"https://nico.ms/{video_id}",
      "fields": [{
        "name": "▶ 再生数",
        "value": f"{view}",
        "inline": True
      }, {
        "name": "📔 コメント数",
        "value": f"{comment}",
        "inline": True
      }, {
        "name": "🖊️ マイリス数",
        "value": f"{mylist}",
        "inline": True
      }],
      "author": {
        "name": f"{author_name}",
        "icon_url": f"{author_icon}"
      },
      "timestamp":
      f"{timestamp}",
      "thumbnail": {
        "url": f"{video_img}"
      }
    }]
  })
  requests.post(os.getenv('WEBHOOK_URL'), json.dumps(discord), headers=DISCORD_HEADER)
  gas = {
      "id": np_id,
      "timestamp": timestamp,
      "title": title,
      "video_id": video_id,
      "view_count": view,
      "comment_count": comment,
      "mylist_count": mylist,
      "video_img": video_img,
      "author_name": author_name,
      "author_icon": author_icon,
      "reasons": reasons,
      "end_time": end_time_str
    }
  requests.post(os.getenv('SP_SH'), data=json.dumps(gas))

while True:
  row_data = {}
  data = {}
  duration = 0
  try:
    row_data = requests.get(NOW_PLAYING_API_URL)
    data = row_data.json()
    duration = data['msec_duration']
  except:
    try:
      print('2')
      row_data = requests.get(NOW_PLAYING_API_URL_TWO)
      data = row_data.json()
      duration = data['msec_duration']
    except:
      print('API error')
      disco = {
        "content": "<@653785595075887104>\nAPI エラーを確認\n10秒遅延します。",
        "embeds": None,
        "username": "Kiiteitte",
        "avatar_url": "https://pbs.twimg.com/profile_images/1584526973505634304/M686vgg3_400x400.jpg",
        "attachments": []
      }
      requests.post(os.getenv('WEBHOOK_URL'),
                    json.dumps(disco),
                    headers=DISCORD_HEADER)
      time.sleep(10)
  start_time = datetime.datetime.fromisoformat(data['start_time'])
  timezone = datetime.timezone(datetime.timedelta(hours=9))
  now_time = datetime.datetime.now(timezone)
  wait_time = (start_time - now_time).total_seconds() + (duration / 1000)
  post_discord(data)
  # check_stage(data)
  # time.sleep(wait_time-10)
  # check_stage(data)
  now_time = datetime.datetime.now(timezone)
  wait_time = (start_time - now_time).total_seconds() + (duration / 1000) + 2
  time.sleep(wait_time)
