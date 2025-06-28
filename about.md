# Filmarks Scraper

このスクリプトは、[Filmarks](https://filmarks.com/) のユーザーページから「Clip!」した映画のリストをスクレイピングし、JSON形式で保存するためのツールです。

## 必要なライブラリ

このスクリプトを実行するには、以下のPythonライブラリが必要です。

- `requests`: HTTPリクエストを送信するために使用します。
- `beautifulsoup4`: HTMLを解析し、データを抽出するために使用します。

これらのライブラリは、`pip` を使ってインストールできます。

```bash
pip install requests beautifulsoup4
```

## 使い方

スクリプトはコマンドラインから実行します。基本的なコマンドは以下の通りです。

```bash
python list.py [FilmarksのURL]
```

**例:**

```bash
python list.py "https://filmarks.com/users/your_user_id/clips"
```

実行すると、スクレイピングが開始され、デフォルトでは `movies.json` というファイル名で結果が保存されます。

## オプション

### `-o` / `--output`

出力するJSONファイルの名前を指定します。

**例:**

```bash
python list.py "https://filmarks.com/users/your_user_id/clips" -o my_movies.json
```

この場合、`my_movies.json` という名前でファイルが作成されます。
