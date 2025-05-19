import csv
import random

NUM_USERS = 30
OUTPUT_FILE = "user_data.csv"

def generate_activity_threshold():
    # Randomize hourly activity between 0.1 and 0.9 with a daily pattern
    morning = [round(random.uniform(0.2, 0.5), 2) for _ in range(6)]     # 0–5 AM
    day = [round(random.uniform(0.5, 0.9), 2) for _ in range(8)]         # 6 AM–1 PM
    evening = [round(random.uniform(0.4, 0.8), 2) for _ in range(6)]     # 2 PM–7 PM
    night = [round(random.uniform(0.2, 0.6), 2) for _ in range(4)]       # 8 PM–11 PM
    return morning + day + evening + night  # 24-hour list

def generate_users():
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["agent_id", "username", "is_controllable", "active_threshold"])

        for i in range(1, NUM_USERS + 1):
            agent_id = i
            username = f"user{i}"
            is_controllable = "False"
            threshold = generate_activity_threshold()
            writer.writerow([agent_id, username, is_controllable, str(threshold)])

    print(f"✅ Generated {NUM_USERS} users in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_users()
import csv
import random
from faker import Faker

fake = Faker()
topics = ["Politics", "Sports", "Technology", "Health", "Entertainment"]

def generate_users(n=30, output_file="user_data.csv"):
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "name", "interest"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(n):
            writer.writerow({
                "id": f"user_{i}",
                "name": fake.name(),
                "interest": random.choice(topics)
            })

if __name__ == "__main__":
    generate_users()
