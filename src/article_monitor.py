import argparse
import hashlib
import json
import sqlite3
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "sources.json"
DB_FILE = ROOT / "data" / "articles.db"


class ArticleMonitor:
    def __init__(self):
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(DB_FILE)
        self.db.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS source_state (
                source_name TEXT PRIMARY KEY,
                initialized INTEGER NOT NULL DEFAULT 0,
                last_checked TEXT
            );

            CREATE TABLE IF NOT EXISTS articles (
                article_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                published_at TEXT,
                discovered_at TEXT NOT NULL,
                notified INTEGER NOT NULL DEFAULT 0
            );
        """)
        self.db.commit()

    @staticmethod
    def _article_id(guid, link):
        value = guid or link
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def fetch_feed(self, source):
        request = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "InvestmentMonitor/1.0"}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        articles = []

        for item in root.findall("./channel/item"):
            title = item.findtext("title")
            link = item.findtext("link")
            published = item.findtext("pubDate")
            guid = item.findtext("guid")

            if not title or not link:
                continue

            articles.append({
                "article_id": self._article_id(guid, link),
                "title": title.strip(),
                "link": link.strip(),
                "published_at": published,
            })

        return articles

    def check_source(self, source):
        name = source["name"]
        articles = self.fetch_feed(source)
        now = datetime.now(timezone.utc).isoformat()

        state = self.db.execute(
            "SELECT initialized FROM source_state WHERE source_name = ?",
            (name,)
        ).fetchone()

        first_run = state is None or not state["initialized"]

        added = 0

        for article in articles:
            self.db.execute("""
                INSERT OR IGNORE INTO articles
                (article_id, source_name, title, link,
                 published_at, discovered_at, notified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                article["article_id"],
                name,
                article["title"],
                article["link"],
                article["published_at"],
                now,
                1 if first_run else 0,
            ))

            if self.db.execute("SELECT changes()").fetchone()[0]:
                added += 1

        if articles:
            self.db.execute("""
                INSERT INTO source_state
                (source_name, initialized, last_checked)
                VALUES (?, 1, ?)
                ON CONFLICT(source_name) DO UPDATE SET
                    initialized = 1,
                    last_checked = excluded.last_checked
            """, (name, now))

        self.db.commit()

        return {
            "first_run": first_run and bool(articles),
            "feed_count": len(articles),
            "added": added,
        }

    def pending_articles(self, source_name, limit=20):
        return self.db.execute("""
            SELECT * FROM articles
            WHERE source_name = ? AND notified = 0
            ORDER BY discovered_at ASC
            LIMIT ?
        """, (source_name, limit)).fetchall()

    def mark_notified(self, article_id):
        self.db.execute(
            "UPDATE articles SET notified = 1 WHERE article_id = ?",
            (article_id,)
        )
        self.db.commit()

    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    with CONFIG_FILE.open(encoding="utf-8") as file:
        config = json.load(file)

    monitor = ArticleMonitor()

    try:
        for source in config["sources"]:
            if not source.get("enabled", False):
                continue

            print(f"\nChecking: {source['name']}")

            try:
                result = monitor.check_source(source)

                print(f"Feed articles found: {result['feed_count']}")
                print(f"New records stored: {result['added']}")

                if result["first_run"]:
                    print("Initial baseline established.")
                    print("Existing articles registered silently.")
                else:
                    pending = monitor.pending_articles(
                        source["name"],
                        source.get("max_articles_per_check", 20)
                    )
                    print(f"Articles awaiting notification: {len(pending)}")

            except Exception as error:
                print(f"ERROR: {error}")

    finally:
        monitor.close()


if __name__ == "__main__":
    main()
