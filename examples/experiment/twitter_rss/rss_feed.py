import asyncio
import aiohttp
import xmltodict
import json
import csv
from datetime import datetime, timezone
from dateutil import parser as date_parser

# === CONFIGURATION ===
RSS_FEED_URL = "https://timesofindia.indiatimes.com/rssfeedmostrecent.cms"
POLL_INTERVAL_SEC = 60
JSON_OUTPUT_FILE = "examples/experiment/twitter_rss/live_rss_feed.json"
CSV_OUTPUT_FILE = "examples/experiment/twitter_rss/live_rss_feed.csv"
MAX_ENTRIES = 30

# === Load existing JSON file ===
async def load_existing():
    try:
        with open(JSON_OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# === Save both JSON and CSV ===
def json_to_csv(json_data, csv_file):
    keys = ["id", "title", "link", "description", "pubDate", "fetched_at"]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(json_data)

async def save_all(entries):
    # Assign unique IDs
    for i, entry in enumerate(entries, start=1):
        entry["id"] = i
    with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    json_to_csv(entries, CSV_OUTPUT_FILE)

# === Parse time for sorting ===
def parse_time(entry):
    try:
        return date_parser.parse(entry.get("pubDate") or entry.get("fetched_at"))
    except Exception:
        return datetime.now(timezone.utc)

# === Fetch and extract items from feed ===
async def fetch_and_extract(session):
    async with session.get(RSS_FEED_URL) as resp:
        resp.raise_for_status()
        body = await resp.read()

    rss = xmltodict.parse(body)
    items = rss.get("rss", {}).get("channel", {}).get("item", [])
    out = []
    for it in items:
        out.append({
            "title":       it.get("title"),
            "link":        it.get("link"),
            "description": it.get("description"),
            "pubDate":     it.get("pubDate")
        })
    return out

# === Main loop ===
async def main():
    seen = {}  # map link -> True
    all_entries = await load_existing()
    for e in all_entries:
        seen[e["link"]] = True

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                latest = await fetch_and_extract(session)
                new_found = False

                for entry in latest:
                    if entry["link"] not in seen:
                        seen[entry["link"]] = True
                        entry["fetched_at"] = datetime.now(timezone.utc).isoformat()
                        all_entries.append(entry)
                        new_found = True

                if new_found:
                    # Sort by pubDate (or fallback to fetched_at), newest first
                    all_entries.sort(key=parse_time, reverse=True)
                    all_entries = all_entries[:MAX_ENTRIES]
                    await save_all(all_entries)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 New items saved – total {len(all_entries)} entries.")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ No new items.")

            except Exception as e:
                print(f"⚠️  Error fetching RSS: {e!r}")

            await asyncio.sleep(POLL_INTERVAL_SEC)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👉 Exiting…")
