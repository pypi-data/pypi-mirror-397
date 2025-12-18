"""Tests for PettingZoo compatible API"""

import pytest
import numpy as np


def test_env_creation():
    """Test creating PettingZoo environment"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=1, num_orange=1)

    assert env.num_blue == 1
    assert env.num_orange == 1
    assert len(env.possible_agents) == 2
    assert "blue_0" in env.possible_agents
    assert "orange_0" in env.possible_agents


def test_env_reset():
    """Test environment reset"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=2, num_orange=2)
    observations, infos = env.reset(seed=42)

    # Check agents are active
    assert len(env.agents) == 4
    assert env.num_agents == 4

    # Check observations
    assert len(observations) == 4
    for agent in env.agents:
        assert agent in observations
        assert observations[agent].shape == (73,)  # Expected observation size
        assert isinstance(observations[agent], np.ndarray)

    # Check infos
    assert len(infos) == 4


def test_observation_space():
    """Test observation space"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=1, num_orange=1)
    env.reset()

    for agent in env.possible_agents:
        obs_space = env.observation_space(agent)
        assert obs_space.shape == (73,)
        assert obs_space.dtype == np.float32


def test_action_space():
    """Test action space"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=1, num_orange=1)
    env.reset()

    for agent in env.possible_agents:
        act_space = env.action_space(agent)
        assert act_space.shape == (
            8,
        )  # throttle, steer, pitch, yaw, roll, jump, boost, handbrake
        assert act_space.dtype == np.float32


def test_step():
    """Test environment step"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=1, num_orange=1)
    env.reset(seed=42)

    # Sample actions
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}

    # Step
    observations, rewards, terminations, truncations, infos = env.step(actions)

    # Check return types
    assert isinstance(observations, dict)
    assert isinstance(rewards, dict)
    assert isinstance(terminations, dict)
    assert isinstance(truncations, dict)
    assert isinstance(infos, dict)

    # Check all agents present
    for agent in env.agents if env.agents else env.possible_agents:
        if agent in observations:
            assert observations[agent].shape == (73,)
        assert agent in rewards
        assert isinstance(rewards[agent], (float, np.floating))
        assert agent in terminations
        assert agent in truncations


def test_multiple_steps():
    """Test multiple environment steps"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=1, num_orange=1)
    env.reset(seed=123)

    for i in range(100):
        if not env.agents:
            break

        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        observations, rewards, terminations, truncations, infos = env.step(actions)

        # Verify info contains expected keys
        for agent in infos:
            assert "ball_pos" in infos[agent]
            assert "goal_scored" in infos[agent]
            assert "tick_count" in infos[agent]


def test_goal_termination():
    """Test that scoring a goal terminates episode"""
    from pettingzoo_env import parallel_env
    import nitro as rs

    env = parallel_env(num_blue=1, num_orange=1)
    env.reset()

    # Put ball in goal
    ball_state = env.arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 5500, 100)  # In orange goal
    env.arena.ball.set_state(ball_state)

    # Step
    actions = {
        agent: np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)
        for agent in env.agents
    }
    observations, rewards, terminations, truncations, infos = env.step(actions)

    # Episode should terminate
    if env.arena.is_ball_scored():
        assert all(terminations.values())
        assert len(env.agents) == 0


def test_time_limit_truncation():
    """Test that time limit truncates episode"""
    from pettingzoo_env import parallel_env

    # Very short time limit
    env = parallel_env(num_blue=1, num_orange=1, time_limit_seconds=0.5)
    env.reset()

    # Step until time limit
    max_steps = int(0.5 * 120)  # 0.5 seconds at 120 ticks/sec

    for i in range(max_steps + 10):
        if not env.agents:
            break

        actions = {agent: np.zeros(8, dtype=np.float32) for agent in env.agents}
        observations, rewards, terminations, truncations, infos = env.step(actions)

    # Episode should have ended due to time limit
    assert len(env.agents) == 0


def test_2v2_game():
    """Test 2v2 game setup"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=2, num_orange=2)
    observations, infos = env.reset()

    assert len(env.agents) == 4
    assert "blue_0" in env.agents
    assert "blue_1" in env.agents
    assert "orange_0" in env.agents
    assert "orange_1" in env.agents

    # All agents should have observations
    assert len(observations) == 4


def test_3v3_game():
    """Test 3v3 game setup"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=3, num_orange=3)
    observations, infos = env.reset()

    assert len(env.agents) == 6
    assert env.num_agents == 6
    assert env.max_num_agents == 6


def test_different_game_modes():
    """Test different game modes"""
    from pettingzoo_env import parallel_env
    import nitro as rs

    for game_mode in [rs.GameMode.SOCCAR, rs.GameMode.HOOPS]:
        env = parallel_env(num_blue=1, num_orange=1, game_mode=game_mode)
        observations, infos = env.reset()

        assert len(observations) == 2
        assert env.arena.game_mode == game_mode


def test_deterministic_reset():
    """Test that seeded resets are deterministic"""
    from pettingzoo_env import parallel_env

    env1 = parallel_env(num_blue=1, num_orange=1)
    obs1, _ = env1.reset(seed=42)

    env2 = parallel_env(num_blue=1, num_orange=1)
    obs2, _ = env2.reset(seed=42)

    # Observations should be identical
    for agent in env1.agents:
        assert np.allclose(obs1[agent], obs2[agent])


def test_state_function():
    """Test global state function"""
    from pettingzoo_env import parallel_env

    env = parallel_env(num_blue=2, num_orange=1)
    env.reset()

    state = env.state()

    # State should be concatenation of all agent observations
    expected_size = 73 * 3  # 3 agents * 73 obs each
    assert state.shape == (expected_size,)
