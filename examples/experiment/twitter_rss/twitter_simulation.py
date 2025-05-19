import json
import pandas as pd
import random

# Load RSS Feed
with open("examples/experiment/twitter_rss/live_rss_feed.json") as f:
    feed = json.load(f)

# Load User Data
users = pd.read_csv("examples/experiment/twitter_rss/user_data.csv").to_dict(orient="records")

# Simulate Posts
print("\n--- Simulated Twitter Feed ---\n")
for user in users:
    article = random.choice(feed)
    print(f"{user['name']} [{user['interest']}] tweets:\n  {article['title']} \n  {article['link']}\n")

# Optional: Simulate Likes
print("\n--- Simulated Likes ---\n")
for user in users:
    if random.random() < 0.3:
        liked_article = random.choice(feed)
        print(f"{user['name']} liked: {liked_article['title']}")
