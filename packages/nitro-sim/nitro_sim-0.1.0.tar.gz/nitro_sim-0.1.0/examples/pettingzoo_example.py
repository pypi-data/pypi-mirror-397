"""Example using PettingZoo API for multi-agent RL training"""

from pettingzoo_env import parallel_env
import numpy as np


def random_policy(observation, agent_id):
    """Random policy for demonstration"""
    # In a real scenario, this would be your trained RL agent
    action = np.random.uniform(-1, 1, size=8)
    action[5:] = np.random.randint(
        0, 2, size=3
    )  # Binary actions for jump/boost/handbrake
    return action.astype(np.float32)


def main():
    # Create a 2v2 Rocket League environment
    env = parallel_env(
        num_blue=2,
        num_orange=2,
        time_limit_seconds=60.0,  # 1 minute episodes
    )

    print("=== PettingZoo Rocket League Environment ===\n")
    print(f"Agents: {env.possible_agents}")
    print(f"Observation space: {env.observation_space('blue_0')}")
    print(f"Action space: {env.action_space('blue_0')}")
    print()

    # Run 3 episodes
    for episode in range(3):
        print(f"Episode {episode + 1}")
        print("-" * 40)

        # Reset environment
        observations, infos = env.reset(seed=episode)

        episode_rewards = {agent: 0.0 for agent in env.agents}
        step_count = 0

        # Run episode
        while env.agents:
            # Get actions from policy for each agent
            actions = {
                agent: random_policy(observations[agent], agent) for agent in env.agents
            }

            # Step environment
            observations, rewards, terminations, truncations, infos = env.step(actions)

            # Accumulate rewards
            for agent in rewards:
                episode_rewards[agent] += rewards[agent]

            step_count += 1

            # Print status every 120 steps (1 second)
            if step_count % 120 == 0:
                ball_pos = infos[env.agents[0]]["ball_pos"] if env.agents else [0, 0, 0]
                print(
                    f"  Step {step_count}: Ball at ({ball_pos[0]:.0f}, {ball_pos[1]:.0f}, {ball_pos[2]:.0f})"
                )

        # Episode finished
        print(f"  Episode ended after {step_count} steps")
        print(f"  Final rewards: {episode_rewards}")
        print()

    env.close()
    print("✓ Training complete!")


if __name__ == "__main__":
    main()
