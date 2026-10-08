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

#気象庁の発表時刻を取得　（例: 2026-10-08T17:00:00:00+09.00 -> 10/08 17:00発表）
report_dt = datetime.fromisoformat(data[0]["reportDatetime"])
report_str = report_dt.strftime("%m/%d %H:%M発表")

time_series = data[0]["timeSeries"]

# 地域名と天気概況を取得
weather_times = time_series[0]["timeDefines"]
area_data = time_series[0]["areas"][0]
area_name = area_data["area"]["name"]
weathers = area_data["weathers"]

weather_lines = []
#直近2日分（今日・明日など）の天気を日時付きで並べる
for t, w in zip(weather_times[:2], weathers[:2]):
    dt = datatime.fromisoformat(t)
    w_clean = w.replace(" "," ")
    weather_lines.append(f" ・{dt.strftime('%m/%d')}: {w_clean}")
weather_str = "\n".join(weather_lines)


# 降水確率を取得（当日分）
pops_data = time_series[1]["timeDefines"]
pops = time_series[1]["areas"][0]["pops"]

pop_items = []
for t, p in zip(pop_times[:4], pops[:4]):
    dt = datetime.fromisoformat(t)
    start_h = dt.hour
    end_h = start_h + 6
    pop_items.append(f"{dt.strftime('%d日')}{start_h:02d}-{end_h:02d}時:`{p}%`")
pops_str = " / ".join(pop_items)

# 3. 気温（対象日・朝/昼の区分とセットで取得）
temp_times = time_series[2]["timeDefines"]
temps = time_series[2]["areas"][0].get("temps", [])

temp_items = []
# 気象庁の仕様で同じ数値が重複して入る場合があるため除外しつつ整形
seen = set()
for t, temp in zip(temp_times, temps):
    key = (t, temp)
    if key in seen:
        continue
    seen.add(key)
    dt = datetime.fromisoformat(t)
    # 00:00は朝の最低気温、09:00は日中の最高気温を表す仕様
    label = "最低(朝)" if dt.hour == 0 else "最高(昼)"
    temp_items.append(f"{dt.strftime('%m/%d')} {label}: `{temp}℃`")

temp_str = " / ".join(temp_items) if temp_items else "データなし"

# Discordに送るメッセージの組み立て
content = (
    f"☀️ **天気予報（{area_name}）** _{report_str}_\n"
    f"**【天気】**\n{weather_lines[0]}\n{weather_lines[1] if len(weather_lines) > 1 else ''}\n"
    f"**【気温】**\n ・{temp_str}\n"
    f"**【降水確率】**\n ・{pops_str}"
)

message = {"content": content}

# Discordへ送信
req_discord = urllib.request.Request(
    WEBHOOK_URL,
    data=json.dumps(message).encode("utf-8"),
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)


