import asyncio
import os
import pandas as pd
import random
from datetime import datetime
from pathlib import Path
from oasis.clock.clock import Clock
from oasis.social_platform.channel import Channel
from oasis.social_platform.platform import Platform
from oasis.social_agent.agents_generator import generate_agents
from oasis.social_platform.typing import ActionType

import logging

# Logging setup
social_log = logging.getLogger("social")
social_log.setLevel(logging.INFO)
social_log.addHandler(logging.StreamHandler())

# Paths (update these paths as per your project structure)
RSS_FEED_PATH = "examples/experiment/twitter_rss/live_rss_feed.csv"  # CSV format
USER_PROFILE_PATH = "examples/experiment/twitter_rss/user_data.csv"
DEFAULT_DB_PATH = ":memory:"

async def simulate_twitter(
    db_path=DEFAULT_DB_PATH,
    rss_path=RSS_FEED_PATH,
    user_path=USER_PROFILE_PATH,
    num_timesteps=5,
    clock_factor=60,
):
    # Remove DB file if file-based and exists
    if db_path != ":memory:" and os.path.exists(db_path):
        os.remove(db_path)
    Path(os.path.dirname(db_path) or ".").mkdir(parents=True, exist_ok=True)

    # Read and clean RSS feed CSV
    try:
        rss_df = pd.read_csv(rss_path).fillna("")
        title = rss_df.iloc[0]["title"]
        pub_date = rss_df[rss_df["title"] == title].iloc[0]["pubDate"]
        source_post_time = pub_date.split(" ")[1]  # Assumes format like "Wed, 20 May 2025 13:45:00"
        start_hour = int(source_post_time.split(":")[0]) + float(int(source_post_time.split(":")[1]) / 60)
    except Exception as e:
        social_log.warning(f"Couldn't parse start time from RSS: {e}. Using default 1PM.")
        start_hour = 13

    start_time = datetime.now()
    clock = Clock(k=clock_factor)
    twitter_channel = Channel()
    infra = Platform(
        db_path=db_path,
        channel=twitter_channel,
        sandbox_clock=clock,
        start_time=start_time,
        recsys_type="twhin-bert",
        refresh_rec_post_count=2,
        max_rec_post_len=2,
        following_post_count=3,
    )

    # Start platform task
    twitter_task = asyncio.create_task(infra.running())

    # Generate agents from user data CSV
    agent_graph = await generate_agents(
        agent_info_path=user_path,
        twitter_channel=twitter_channel,
        start_time=start_time,
        model=None,
        recsys_type="twhin-bert",
        twitter=infra,
    )

    # Run simulation steps
    for timestep in range(1, num_timesteps + 1):
        clock.time_step = timestep * 3
        sim_hour = start_hour + 0.05 * timestep
        print(f"\nTimestep {timestep} | Sim hour: {sim_hour:.2f}")

        tasks = []
        for node_id, agent in agent_graph.get_agents():
            if not agent.user_info.is_controllable:
                hour_index = int(sim_hour % 24)
                threshold_list = agent.user_info.profile.get("other_info", {}).get("active_threshold", [])
                threshold = threshold_list[hour_index] if hour_index < len(threshold_list) else 0.5
                if random.random() < threshold:
                    tasks.append(agent.perform_action_by_llm())
            else:
                await agent.perform_action_by_hci()

        await asyncio.gather(*tasks)

    # Signal simulation end and wait for platform to clean up
    await twitter_channel.write_to_receive_queue((None, None, ActionType.EXIT))
    await twitter_task

if __name__ == "__main__":
    asyncio.run(simulate_twitter())
    social_log.info("✅ Simulation complete.")
