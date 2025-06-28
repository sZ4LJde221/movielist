import requests
from bs4 import BeautifulSoup
import json
import time
import random

BASE_URL = "https://filmarks.com/users/tananeet25/clips"
OUTPUT_JSON = "movies.json"

# リクエスト間の待機時間（秒）
MIN_DELAY = 2
MAX_DELAY = 5

movies = []
page = 1
while True:
    params = {"page": page}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ScraperBot/1.0)"}

    response = requests.get(BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.c-content-item")
    if not items:
        break

    for item in items:
        title_tag = item.select_one("h3.c-content-item__title a")
        title = title_tag.get_text(strip=True) if title_tag else None

        star_tag = item.select_one(
            ".c-content-item-infobar__item--star .c-content-item-infobar__body"
        )
        rating = star_tag.get_text(strip=True) if star_tag else None

        movies.append({
            "title": title,
            "rating": rating,
        })

    # 次ページへ移動する前にランダムな待機
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"ページ {page} 処理完了、{delay:.1f} 秒待機します...")
    time.sleep(delay)

    page += 1

# 結果をJSONで保存
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(movies, f, ensure_ascii=False, indent=2)

print(f"取得完了: {len(movies)} 件の映画情報を{OUTPUT_JSON}に保存しました。")
