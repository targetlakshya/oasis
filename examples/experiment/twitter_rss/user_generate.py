import pandas as pd
import string
import random
import csv

# File paths
rss_feed_path = "examples/experiment/twitter_rss/live_rss_feed.csv"
user_data_path = "examples/experiment/twitter_rss/user_data.csv"

# Load RSS data
rss_df = pd.read_csv(rss_feed_path).fillna("")

# Clean/sanitize titles
def sanitize_title(title):
    allowed_chars = string.ascii_letters + string.digits + " "
    return ''.join(c for c in title if c in allowed_chars).strip()

# Generate sample user characteristics
user_chars = ["friendly", "curious", "sarcastic", "analytical", "outspoken"]

# Create user data
users = []
all_sanitized_titles = [sanitize_title(t)[:100] for t in rss_df["title"] if isinstance(t, str) and sanitize_title(t)]

for i, title in enumerate(all_sanitized_titles, start=1):
    if not title:
        continue  # Skip empty titles

    user_id = i
    name = f"User{user_id}"
    username = f"user_{user_id}"
    following_ids = random.sample(range(1, i), k=min(i - 1, random.randint(1, 3))) if i > 1 else []

    other_titles = all_sanitized_titles[:i-1] + all_sanitized_titles[i:]  # Exclude current title
    previous_tweets = random.sample(other_titles, k=min(len(other_titles), 3)) if other_titles else []

    user = {
        "user_id": user_id,
        "name": name,
        "username": username,
        "following_agentid_list": str(following_ids),
        "previous_tweets": str(previous_tweets),
        "user_char": random.choice(user_chars),
        "description": title[:100]  # Limit to 100 characters
    }
    users.append(user)

# Write to CSV
with open(user_data_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "user_id", "name", "username", "following_agentid_list",
        "previous_tweets", "user_char", "description"
    ])
    writer.writeheader()
    for user in users:
        writer.writerow(user)

print(f"✅ Generated {len(users)} users in {user_data_path}")
