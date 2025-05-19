import asyncio
import json
import os
import random
from datetime import datetime
from typing import List

# Simulated simple LLM model class for text generation
class DummyLLM:
    async def generate_text(self, prompt: str) -> str:
        # Dummy reply just echoes prompt's key part (replace with real LLM calls)
        await asyncio.sleep(0.1)
        return f"Tweet about: {prompt.split(':')[1].strip()}"

# Agent class
class Agent:
    def __init__(self, user_id: int, interests: List[str], llm):
        self.user_id = user_id
        self.interests = interests
        self.llm = llm
        self.memory = []  # To store RSS articles relevant to this agent

    def load_rss_articles(self, rss_articles: List[dict]):
        # Filter articles by matching interests (title contains interest keyword)
        filtered = [
            art for art in rss_articles 
            if any(interest.lower() in art['title'].lower() for interest in self.interests)
        ]
        self.memory = filtered

    async def perform_action(self):
        if not self.memory:
            print(f"Agent {self.user_id}: No relevant articles to tweet about.")
            return

        article = random.choice(self.memory)
        prompt = f"Write a tweet about: {article['title']}"
        tweet = await self.llm.generate_text(prompt)
        self.post_tweet(tweet)

    def post_tweet(self, tweet: str):
        print(f"[Agent {self.user_id} Tweet]: {tweet}")

# Simulation main function
async def run_simulation(num_agents=5, num_timesteps=3, rss_feed_file="examples/experiment/twitter_rss/live_rss_feed.json"):

    # Load RSS articles from JSON file
    if not os.path.exists(rss_feed_file):
        print("RSS feed file not found!")
        return
    with open(rss_feed_file, "r") as f:
        rss_articles = json.load(f)  # Expect list of dicts with at least 'title'

    llm = DummyLLM()

    # Create agents with random interests (from a fixed pool)
    interests_pool = ["Technology", "Politics", "Sports", "Economy", "Health"]
    agents = []
    for i in range(num_agents):
        interests = random.sample(interests_pool, k=2)
        agent = Agent(user_id=i, interests=interests, llm=llm)
        agent.load_rss_articles(rss_articles)
        agents.append(agent)
        print(f"Created Agent {i} with interests {interests}")

    print("\nStarting simulation...\n")

    # Run timesteps
    for timestep in range(1, num_timesteps + 1):
        print(f"--- Timestep {timestep} ---")
        tasks = [agent.perform_action() for agent in agents]
        await asyncio.gather(*tasks)
        print("\n")

if __name__ == "__main__":
    asyncio.run(run_simulation())
