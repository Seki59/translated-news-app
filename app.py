import feedparser
import openai
import datetime
from flask import Flask, jsonify
import os

# --- ChatGPT APIキー（環境変数から取得） ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- ニュースRSS URL一覧 ---
RSS_FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "APNews": "https://apnews.com/rss"
}

# --- 英語→日本語 翻訳関数（ChatGPT API使用） ---
def translate_to_japanese(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # または "gpt-4o"
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following English text into natural Japanese."},
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[翻訳エラー]: {e}"

# --- RSS取得 & 翻訳処理 ---
def fetch_and_translate():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # 各サイトから最大10記事
            translated_title = translate_to_japanese(entry.title)
            translated_summary = translate_to_japanese(entry.summary) if hasattr(entry, "summary") else ""
            articles.append({
                "source": source,
                "title_en": entry.title,
                "title_ja": translated_title,
                "summary_ja": translated_summary,
                "link": entry.link,
                "published": entry.get("published", "")
            })
    # 日付順にソート（≒人気順の代用）
    articles.sort(key=lambda x: x['published'], reverse=True)
    return articles[:10]

# --- Flaskアプリ起動 ---
app = Flask(__name__)

@app.route("/api/news")
def get_news():
    data = fetch_and_translate()
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Renderの環境変数PORTを取得、無ければ5000
    app.run(host="0.0.0.0", port=port, debug=True)
