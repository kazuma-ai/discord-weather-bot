import os
import json
import urllib.request

# 都道府県コード（例: 大阪府 = 270000）
AREA_CODE = "270000"
# GitHub SecretsからWebhook URLを取得
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{AREA_CODE}.json"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req) as res:
    data = json.loads(res.read().decode("utf-8"))

# 地域名と天気概況を取得
time_series = data[0]["timeSeries"]
area_data = time_series[0]["areas"][0]
area_name = area_data["area"]["name"]
today_weather = area_data["weathers"][0].replace(" ", " ")

# 降水確率を取得（当日分）
pops_data = time_series[1]["areas"][0]["pops"]
pops_str = " / ".join([f"{p}%" for p in pops_data[:4]])

# Discordに送るメッセージの組み立て
content = (
    f"☀️ **今日の天気予報（{area_name}）**\n"
    f"・**天気**: {today_weather}\n"
    f"・**降水確率**: {pops_str}"
)

message = {"content": content}

# Discordへ送信
req_discord = urllib.request.Request(
    WEBHOOK_URL,
    data=json.dumps(message).encode("utf-8"),
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)
urllib.request.urlopen(req_discord)
