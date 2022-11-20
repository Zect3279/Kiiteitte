require('dotenv').config();
const axios = require('axios')
const Twitter = require('twitter-lite');

NOW_PLAYING_API_URL = "https://cafe.kiite.jp/api/cafe/now_playing"
NOW_PLAYING_API_URL_TWO = "https://cafeapi.kiite.jp/api/cafe/now_playing"

WEBHOOK_URL = "https://discord.com/api/webhooks/1040902161271365692/GigT6KPtFiod3lMDGoArvfKGdMgTh-kVBkFxu_YT3y5nLYCqyA9gCTJv6AMRqc7RZ1Gu"

const client = new Twitter({
  consumer_key: process.env.API_KEY,
  consumer_secret: process.env.API_SECRET,
  access_token_key: process.env.ACCESS_TOKEN,
  access_token_secret: process.env.ACCESS_TOKEN_SECRET
});

var wait_time = 0

;(async ()=>{
while (true){
  const response = await axios.get(NOW_PLAYING_API_URL)
  const data = response.data
  const duration = data['msec_duration']
  const msg = `♪${data['title']} #${data['video_id']} #Kiite\nKiite Cafeできいてます https://cafe.kiite.jp/ https://nico.ms/${data['video_id']}`
  wait_time = (Date.parse(data['start_time']) - Date.parse(new Date())) + duration + 2000;
  await axios.post(WEBHOOK_URL, {
    "username": "Kiiteitte",
    "avatar_url": "https://pbs.twimg.com/profile_images/1584526973505634304/M686vgg3_400x400.jpg",
    "content": null,
    "embeds":[{"title": `♪ ${data['title']}`,"url": `https://nico.ms/${data['video_id']}`,"fields": [{"name": "▶ 再生数","value": `${data['baseinfo']['view_counter']}`,"inline": true},{"name": "📔 コメント数","value": `${data['baseinfo']['comment_num']}`,"inline": true},{"name": "🖊️ マイリス数","value": `${data['baseinfo']['mylist_counter']}`,"inline": true}],"author": {"name": `${data['baseinfo']['user_nickname']}`,"icon_url": `${data['baseinfo']['user_icon_url']}`},"timestamp": `${data['start_time']}`,"thumbnail": {"url": `${data['baseinfo']['thumbnail_url']}`}}]
  })
  await client.post('statuses/update', {
    status: msg
  });

  console.log(wait_time)
  await new Promise((resolve) => setTimeout(resolve, wait_time))
}
})()
