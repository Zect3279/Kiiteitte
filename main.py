from linebot import LineBotApi
from linebot.models import TextSendMessage
import json
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
import time

load_dotenv()

line_bot_api = LineBotApi(os.getenv('LI_NE'))
line_user_id = os.getenv('US_ID')
messages = TextSendMessage(text="Kiiteitteの停止を確認しました。\n直ちに再起動してください。")

next_time = time.time()

while True:
    uj = json.loads(requests.get("https://cafeapi.kiite.jp/api/cafe/users?limit=300").text)

    np_row = json.loads(requests.get(os.getenv('NP_URL')).text)
    np_id = np_row["lastA"]
    np_reasons = json.loads(np_row["lastK"])
    np_end = datetime.fromisoformat(np_row["lastL"])

    now = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    if np_end <= now:
        print("error")
        line_bot_api.push_message(line_user_id, messages=messages)
        time.sleep()
        continue
    else:
        comments = json.loads(requests.get("https://cafeapi.kiite.jp/api/cafe/user_comments").text)
        new_fav = json.loads(requests.get(f"https://cafeapi.kiite.jp/api/cafe/new_fav?id={np_id}").text)
        rotates = json.loads(requests.get(f"https://cafeapi.kiite.jp/api/cafe/user_gestures?id={np_id}").text)
        fav_reason = [item["user_id"] for item in np_reasons if item["type"] == "favorite"]

        place_list = []
        for item in uj:
            id = item["user_id"]
            r = any(str(id) in key for key in rotates.keys()) or None
            f = (id in new_fav or id in fav_reason) or None
            pre_com = [c for c in comments if c["user_id"] == id and c["comment"]]
            c = None
            if pre_com:
                c = max(pre_com, key=lambda d: d["created_at"])["comment"]
            v = item["user_va"]["v"]
            a = item["user_va"]["a"]
            data = {"v": v, "a": a, "r": r, "f": f, "c": c}
            data = {k: v for k, v in data.items() if v is not None}
            place_list.append(data)

        now = str(datetime.now())

        gas = {
        "timestamp": now,
        "id": np_id,
        "user_count": len(place_list),
        "rotate_count": len(rotates),
        "new_fav_count": len(new_fav),
        "fav_count": len(new_fav)+len(fav_reason),
        "pcr": place_list
        }
        requests.post(os.getenv('SP_SH'), data=json.dumps(gas))
        print(now)

    # 次の処理開始時刻を計算
    next_time += 20

    # 次の処理開始時刻まで待機
    sleep_time = next_time - time.time()
    if sleep_time > 0:
        time.sleep(sleep_time)
