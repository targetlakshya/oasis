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

# Logging setup for console output
social_log = logging.getLogger("social")
social_log.setLevel(logging.INFO)
social_log.addHandler(logging.StreamHandler())

# Paths
RSS_FEED_PATH = "examples/experiment/twitter_rss/live_rss_feed.csv"
USER_PROFILE_PATH = "examples/experiment/twitter_rss/user_data1.csv"
DEFAULT_DB_PATH = ":memory:"
OUTPUT_LOG = "examples/experiment/twitter_rss/twitter_simulation_output.log"

async def simulate_twitter(
    db_path=DEFAULT_DB_PATH,
    rss_path=RSS_FEED_PATH,
    user_path=USER_PROFILE_PATH,
    num_timesteps=5,
    clock_factor=60,
):
  
    if db_path != ":memory:" and os.path.exists(db_path):
        os.remove(db_path)
    Path(os.path.dirname(db_path) or ".").mkdir(parents=True, exist_ok=True)

  
    Path(os.path.dirname(OUTPUT_LOG)).mkdir(parents=True, exist_ok=True)

    # Start time extraction from RSS feed
    try:
        rss_df = pd.read_csv(rss_path).fillna("")
        title = rss_df.iloc[0]["title"]
        pub_date = rss_df[rss_df["title"] == title].iloc[0]["pubDate"]
        source_post_time = pub_date.split(" ")[1]
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

    twitter_task = asyncio.create_task(infra.running())

    agent_graph = await generate_agents(
        agent_info_path=user_path,
        twitter_channel=twitter_channel,
        start_time=start_time,
        model=0,
        recsys_type="twhin-bert",
        twitter=infra,
    )   

    collected_responses = []

    for timestep in range(1, num_timesteps + 1):
        clock.time_step = timestep * 3
        sim_hour = start_hour + 0.05 * timestep
        social_log.info(f"\nTimestep {timestep} | Sim hour: {sim_hour:.2f}")

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

        results = await asyncio.gather(*tasks)
        for r in results:
            if r:
                collected_responses.append(r)

    with open(OUTPUT_LOG, "w", encoding="utf-8") as log_file:
        for response in collected_responses:
            log_file.write(str(response) + "\n")
            log_file.write("\n\n")  

    social_log.info(f"✅ Saved {len(collected_responses)} responses to {OUTPUT_LOG}")

    await twitter_channel.write_to_receive_queue((None, None, ActionType.EXIT))
    await twitter_task


if __name__ == "__main__":
    asyncio.run(simulate_twitter())
    social_log.info("✅ Simulation complete.")
