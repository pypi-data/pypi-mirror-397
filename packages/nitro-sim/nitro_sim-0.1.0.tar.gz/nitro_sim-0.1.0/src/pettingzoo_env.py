"""PettingZoo-compatible API for RocketSim"""

from typing import Dict, List, Optional, Any
import numpy as np
from gymnasium import spaces
import nitro as rs


class RocketLeagueParallelEnv:
    """
    PettingZoo Parallel API compatible environment for Rocket League simulation.

    Supports 1v1, 2v2, and 3v3 game modes with configurable team sizes.

    Example:
        >>> env = RocketLeagueParallelEnv(num_blue=2, num_orange=2)
        >>> observations, infos = env.reset()
        >>> while env.agents:
        ...     actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        ...     observations, rewards, terminations, truncations, infos = env.step(actions)
    """

    metadata = {"render_modes": ["human", "rgb_array"], "name": "rocket_league_v0"}

    def __init__(
        self,
        num_blue: int = 1,
        num_orange: int = 1,
        game_mode: rs.GameMode = rs.GameMode.SOCCAR,
        tick_rate: float = 120.0,
        time_limit_seconds: float = 300.0,
        render_mode: Optional[str] = None,
        collision_meshes_path: str = "collision_meshes",
    ):
        """
        Initialize Rocket League environment.

        Args:
            num_blue: Number of blue team cars (1-3)
            num_orange: Number of orange team cars (1-3)
            game_mode: Game mode (SOCCAR, HOOPS, etc.)
            tick_rate: Physics simulation tick rate
            time_limit_seconds: Maximum episode length in seconds
            render_mode: "human" or "rgb_array" (not implemented yet)
            collision_meshes_path: Path to RocketSim collision meshes
        """
        # Initialize RocketSim if needed
        if rs.get_stage() != rs.RocketSimStage.INITIALIZED:
            rs.init(collision_meshes_path, silent=True)

        self.num_blue = num_blue
        self.num_orange = num_orange
        self.game_mode = game_mode
        self.tick_rate = tick_rate
        self.time_limit_seconds = time_limit_seconds
        self.max_ticks = int(time_limit_seconds * tick_rate)
        self.render_mode = render_mode

        # Create agent names
        self.possible_agents = [f"blue_{i}" for i in range(num_blue)] + [
            f"orange_{i}" for i in range(num_orange)
        ]
        self.agents = []
        self._agent_to_car: Dict[str, rs.Car] = {}
        self._car_id_to_agent: Dict[int, str] = {}

        # Arena and state
        self.arena: Optional[rs.Arena] = None
        self._tick_count = 0

        # Define observation and action spaces
        self._setup_spaces()

    def _setup_spaces(self):
        """Setup observation and action spaces"""
        # Observation space: [car state (33) + ball state (6) + boost pads (34)]
        # Car state: pos(3) + vel(3) + ang_vel(3) + rot_mat(9) + boost(1) +
        #            is_on_ground(1) + is_supersonic(1) + other flags(12)
        # Ball state: pos(3) + vel(3)
        # Boost pads: 34 pads * [is_active(1)]
        obs_size = 33 + 6 + 34  # Total: 73

        self._observation_spaces = {
            agent: spaces.Box(
                low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32
            )
            for agent in self.possible_agents
        }

        # Action space: [throttle, steer, pitch, yaw, roll, jump, boost, handbrake]
        # Continuous for first 5, discrete for last 3
        # We'll use a Box space with values clamped in step
        self._action_spaces = {
            agent: spaces.Box(
                low=np.array([-1, -1, -1, -1, -1, 0, 0, 0], dtype=np.float32),
                high=np.array([1, 1, 1, 1, 1, 1, 1, 1], dtype=np.float32),
                dtype=np.float32,
            )
            for agent in self.possible_agents
        }

    def observation_space(self, agent: str) -> spaces.Space:
        """Get observation space for agent"""
        return self._observation_spaces[agent]

    def action_space(self, agent: str) -> spaces.Space:
        """Get action space for agent"""
        return self._action_spaces[agent]

    def _get_observation(self, agent: str) -> np.ndarray:
        """Get observation for agent"""
        car = self._agent_to_car[agent]
        car_state = car.get_state()
        ball_state = self.arena.ball.get_state()
        boost_pads = self.arena.get_boost_pads()

        # Car state components
        obs = []

        # Position and velocity
        obs.extend([car_state.pos.x, car_state.pos.y, car_state.pos.z])
        obs.extend([car_state.vel.x, car_state.vel.y, car_state.vel.z])
        obs.extend([car_state.ang_vel.x, car_state.ang_vel.y, car_state.ang_vel.z])

        # Rotation matrix (9 values)
        obs.extend(
            [
                car_state.rot_mat.forward.x,
                car_state.rot_mat.forward.y,
                car_state.rot_mat.forward.z,
                car_state.rot_mat.right.x,
                car_state.rot_mat.right.y,
                car_state.rot_mat.right.z,
                car_state.rot_mat.up.x,
                car_state.rot_mat.up.y,
                car_state.rot_mat.up.z,
            ]
        )

        # Car status
        obs.append(car_state.boost)
        obs.append(float(car_state.is_on_ground))
        obs.append(float(car_state.is_supersonic))
        obs.append(float(car_state.is_jumping))
        obs.append(float(car_state.is_flipping))
        obs.append(float(car_state.has_jumped))
        obs.append(float(car_state.has_double_jumped))
        obs.append(float(car_state.has_flipped))
        obs.append(float(car_state.is_demoed))
        obs.append(car_state.air_time)
        obs.append(car_state.jump_time)
        obs.append(car_state.flip_time)
        obs.extend(
            [
                car_state.flip_rel_torque.x,
                car_state.flip_rel_torque.y,
                car_state.flip_rel_torque.z,
            ]
        )

        # Ball state
        obs.extend([ball_state.pos.x, ball_state.pos.y, ball_state.pos.z])
        obs.extend([ball_state.vel.x, ball_state.vel.y, ball_state.vel.z])

        # Boost pads (34 values: 1 if active, 0 if on cooldown)
        for pad in boost_pads:
            obs.append(float(pad.get_state().is_active))

        return np.array(obs, dtype=np.float32)

    def _get_reward(self, agent: str) -> float:
        """Calculate reward for agent"""
        # Simple reward: positive if ball moving toward opponent goal
        car = self._agent_to_car[agent]
        ball_state = self.arena.ball.get_state()

        # Determine goal direction based on team
        team = car.team
        goal_direction = 1 if team == rs.Team.BLUE else -1

        # Reward for ball velocity toward opponent goal
        ball_vel_y = ball_state.vel.y * goal_direction
        reward = ball_vel_y / 1000.0  # Normalize

        # Bonus for touching ball
        if car.get_state().ball_hit_info.is_valid:
            reward += 0.1

        # Penalty for being demoed
        if car.get_state().is_demoed:
            reward -= 1.0

        return reward

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict] = None
    ) -> tuple[Dict[str, np.ndarray], Dict[str, Dict]]:
        """Reset environment to initial state"""
        if seed is not None:
            np.random.seed(seed)
            kickoff_seed = seed
        else:
            kickoff_seed = -1

        # Create new arena
        self.arena = rs.Arena.create(self.game_mode, tick_rate=self.tick_rate)
        self._tick_count = 0

        # Add cars
        self._agent_to_car = {}
        self._car_id_to_agent = {}

        for i in range(self.num_blue):
            agent_name = f"blue_{i}"
            car = self.arena.add_car(rs.Team.BLUE, rs.CAR_CONFIG_OCTANE)
            self._agent_to_car[agent_name] = car
            self._car_id_to_agent[car.id] = agent_name

        for i in range(self.num_orange):
            agent_name = f"orange_{i}"
            car = self.arena.add_car(rs.Team.ORANGE, rs.CAR_CONFIG_OCTANE)
            self._agent_to_car[agent_name] = car
            self._car_id_to_agent[car.id] = agent_name

        # Reset to kickoff
        self.arena.reset_to_random_kickoff(seed=kickoff_seed)

        # Set active agents
        self.agents = self.possible_agents.copy()

        # Get initial observations
        observations = {agent: self._get_observation(agent) for agent in self.agents}

        infos = {agent: {} for agent in self.agents}

        return observations, infos

    def step(
        self, actions: Dict[str, np.ndarray]
    ) -> tuple[
        Dict[str, np.ndarray],
        Dict[str, float],
        Dict[str, bool],
        Dict[str, bool],
        Dict[str, Dict],
    ]:
        """Execute one step of the environment"""
        # Apply actions to cars
        for agent, action in actions.items():
            if agent not in self._agent_to_car:
                continue

            car = self._agent_to_car[agent]
            controls = car.controls

            # Map action array to controls
            controls.throttle = float(np.clip(action[0], -1, 1))
            controls.steer = float(np.clip(action[1], -1, 1))
            controls.pitch = float(np.clip(action[2], -1, 1))
            controls.yaw = float(np.clip(action[3], -1, 1))
            controls.roll = float(np.clip(action[4], -1, 1))
            controls.jump = bool(action[5] > 0.5)
            controls.boost = bool(action[6] > 0.5)
            controls.handbrake = bool(action[7] > 0.5)

        # Step simulation
        self.arena.step(1)
        self._tick_count += 1

        # Get observations
        observations = {agent: self._get_observation(agent) for agent in self.agents}

        # Calculate rewards
        rewards = {agent: self._get_reward(agent) for agent in self.agents}

        # Check for goal (termination)
        goal_scored = self.arena.is_ball_scored()

        # Check time limit (truncation)
        time_limit_reached = self._tick_count >= self.max_ticks

        terminations = {agent: goal_scored for agent in self.agents}
        truncations = {agent: time_limit_reached for agent in self.agents}

        # Bonus reward for scoring team
        if goal_scored:
            ball_y = self.arena.ball.get_state().pos.y
            scoring_team = rs.Team.ORANGE if ball_y < 0 else rs.Team.BLUE

            for agent in self.agents:
                car = self._agent_to_car[agent]
                if car.team == scoring_team:
                    rewards[agent] += 10.0  # Big reward for scoring
                else:
                    rewards[agent] -= 10.0  # Penalty for being scored on

        infos = {
            agent: {
                "ball_pos": [
                    self.arena.ball.get_state().pos.x,
                    self.arena.ball.get_state().pos.y,
                    self.arena.ball.get_state().pos.z,
                ],
                "goal_scored": goal_scored,
                "tick_count": self._tick_count,
            }
            for agent in self.agents
        }

        # Remove agents if episode ended
        if goal_scored or time_limit_reached:
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def render(self):
        """Render the environment (not implemented)"""
        if self.render_mode == "human":
            # TODO: Add visualization
            pass
        elif self.render_mode == "rgb_array":
            # TODO: Return RGB array
            return None
        return None

    def close(self):
        """Clean up environment resources"""
        self.arena = None
        self.agents = []
        self._agent_to_car = {}
        self._car_id_to_agent = {}

    @property
    def num_agents(self) -> int:
        """Current number of active agents"""
        return len(self.agents)

    @property
    def max_num_agents(self) -> int:
        """Maximum possible number of agents"""
        return len(self.possible_agents)

    def state(self) -> np.ndarray:
        """Global state of the environment"""
        # Return combined state of all agents
        if not self.agents:
            return np.array([])

        states = [self._get_observation(agent) for agent in self.agents]
        return np.concatenate(states)

    def observation_space(self, agent: str) -> spaces.Space:
        """Observation space for agent"""
        return self._observation_spaces[agent]

    def action_space(self, agent: str) -> spaces.Space:
        """Action space for agent"""
        return self._action_spaces[agent]


def parallel_env(
    num_blue: int = 1, num_orange: int = 1, **kwargs
) -> RocketLeagueParallelEnv:
    """
    Factory function to create a RocketLeague parallel environment.

    Args:
        num_blue: Number of blue team cars (1-3)
        num_orange: Number of orange team cars (1-3)
        **kwargs: Additional arguments passed to RocketLeagueParallelEnv

    Returns:
        RocketLeagueParallelEnv instance
    """
    return RocketLeagueParallelEnv(num_blue=num_blue, num_orange=num_orange, **kwargs)
