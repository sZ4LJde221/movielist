import os
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import argparse
import sys
import re
from typing import List, Dict, Optional
from datetime import datetime

# リクエスト間の待機時間（秒）
MIN_DELAY = 2
MAX_DELAY = 5
BASE_DOMAIN = "https://filmarks.com"
# 標準的なブラウザのUser-Agent
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
# エラー時再試行設定
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # 秒
BACKOFF_FACTOR = 2

# 出力用ディレクトリ名
DEFAULT_OUTPUT_DIR = "data"


def get_last_page(session: requests.Session, url: str) -> int:
    resp = session.get(
        url, params={"page": 1}, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=10
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    last_link = soup.select_one("a.c2-pagination__last")
    if not last_link or not last_link.get("href"):
        raise RuntimeError(
            "最終ページのリンクが見つかりません。ページネーションの構造が変更された可能性があります。"
        )
    href = last_link["href"]
    q = href.split("page=")[-1]
    try:
        return int(q)
    except ValueError:
        raise ValueError(f"無効なページ番号 '{q}' が検出されました。")


def scrape_page(
    session: requests.Session, url: str, page: int
) -> List[Dict[str, Optional[str]]]:
    params = {"page": page}
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                print(
                    f"ページ {page} の取得に失敗しました（試行 {attempt}/{MAX_RETRIES}）。エラー: {e}",
                    file=sys.stderr,
                )
                return []
            wait = backoff + random.uniform(0, 1)
            print(
                f"ページ {page} の取得でエラー (試行 {attempt}/{MAX_RETRIES})。{wait:.1f}秒後に再試行します...",
                file=sys.stderr,
            )
            time.sleep(wait)
            backoff *= BACKOFF_FACTOR
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("div.c-content-item")
    if not items:
        print(f"ページ {page} にアイテムが見つかりませんでした。", file=sys.stderr)
    result = []
    for item in items:
        title_tag = item.select_one("h3.c-content-item__title a")
        title = title_tag.get_text(strip=True) if title_tag else None
        rel_link = title_tag.get("href") if title_tag else None
        link = f"{BASE_DOMAIN}{rel_link}" if rel_link else None

        # 評価 (rating) を抽出し、数値以外は空文字にする
        star_tag = item.select_one(
            ".c-content-item-infobar__item--star .c-content-item-infobar__body"
        )
        raw_rating = star_tag.get_text(strip=True) if star_tag else None
        if raw_rating and re.match(r"^\d+(?:\.\d+)?$", raw_rating):
            rating = raw_rating
        else:
            rating = ""

        # ポスター画像のURLを抽出
        img_tag = item.select_one("div.c2-poster-m img")
        image_url = img_tag.get("src") if img_tag and img_tag.get("src") else None

        result.append(
            {
                "title": title,
                "rating": rating,
                "link": link,
                "image_url": image_url,
            }
        )
    return result


def main(base_url: str, output_dir: str):
    # スクリプトの実行時刻を取得
    execution_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

    movies = []
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_json = os.path.join(output_dir, f"movies_{timestamp}.json")
    with requests.Session() as session:
        try:
            last_page = get_last_page(session, base_url)
        except Exception as e:
            print(f"Error determining last page: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"検出した最終ページ: {last_page}")
        for page in range(1, last_page + 1):
            print(f"Scraping page {page}/{last_page}...")
            page_movies = scrape_page(session, base_url, page)
            if not page_movies:
                print(
                    f"ページ {page} でスクレイピング失敗またはデータなし。処理を中断します。",
                    file=sys.stderr,
                )
                break
            movies.extend(page_movies)
            if page < last_page:
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                print(f"ページ {page} 処理完了、{delay:.1f} 秒待機します...")
                time.sleep(delay)

    # JSON 出力用データにメタ情報を追加
    output_data = {
        "metadata": {"executed_at": execution_time, "total_items": len(movies)},
        "movies": movies,
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(
        f"取得完了: {len(movies)} 件の映画情報を {output_json} に保存しました。実行時刻: {execution_time}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        help="ClipページのURL (例: https://filmarks.com/users/your_user_id/clips)",
    )
    parser.add_argument(
        "-d",
        "--dir",
        default=DEFAULT_OUTPUT_DIR,
        help="出力ディレクトリ名 (デフォルト: 'data')",
    )
    args = parser.parse_args()
    main(args.url, args.dir)
