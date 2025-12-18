# nitro-sim Examples

Example scripts demonstrating different features of nitro-sim.

## Running Examples

All examples require collision meshes. They will auto-download on first run, or you can provide a path:

```bash
export ROCKETSIM_COLLISION_MESHES_PATH=path/to/collision_meshes
```

## Available Examples

### test_autocomplete.py

Demonstrates basic usage and IDE autocomplete support:
- Vector math operations
- Car controls and state
- Type hints and IntelliSense

```bash
uv run python examples/test_autocomplete.py
```

### example_advanced.py

Comprehensive example showing advanced features:
- Ball trajectory prediction with `BallPredTracker`
- Game event tracking (shots, goals, saves)
- Arena and event callbacks
- Boost pad monitoring
- Multi-car simulation

```bash
uv run python examples/example_advanced.py
```

### pettingzoo_example.py

Multi-agent RL training example using PettingZoo API:
- 2v2 Rocket League environment
- Compatible with PettingZoo/Gymnasium standards
- Ready for RL frameworks (Stable-Baselines3, RLlib, etc.)
- Demonstrates observation/action spaces
- Episode management with termination/truncation

```bash
uv run python examples/pettingzoo_example.py
```

## For RL Training

The PettingZoo API is compatible with popular RL frameworks:

### Stable-Baselines3

```python
from pettingzoo.utils import parallel_to_aec
from pettingzoo_env import parallel_env
from supersuit import pettingzoo_env_to_vec_env_v1
from stable_baselines3 import PPO

# Wrap environment
parallel_env_instance = parallel_env(num_blue=1, num_orange=1)
aec_env = parallel_to_aec(parallel_env_instance)
vec_env = pettingzoo_env_to_vec_env_v1(aec_env)

# Train
model = PPO("MlpPolicy", vec_env, verbose=1)
model.learn(total_timesteps=100000)
```

### RLlib (Ray)

```python
from ray.rllib.env import PettingZooEnv
from pettingzoo_env import parallel_env

# Register environment
env = PettingZooEnv(parallel_env(num_blue=2, num_orange=2))

# Configure and train with RLlib
config = {
    "env": env,
    "framework": "torch",
    # ... other config
}
```

## Custom Policies

You can easily implement custom policies:

```python
def my_policy(observation):
    # observation is numpy array of shape (73,)
    # Contains: car state (33) + ball state (6) + boost pads (34)
    
    # Extract components
    car_pos = observation[0:3]
    car_vel = observation[3:6]
    ball_pos = observation[33:36]
    ball_vel = observation[36:39]
    
    # Your logic here...
    action = np.array([
        1.0,  # throttle
        0.0,  # steer
        0.0,  # pitch
        0.0,  # yaw
        0.0,  # roll
        0.0,  # jump
        1.0,  # boost
        0.0,  # handbrake
    ])
    
    return action
```

## Environment Details

**Observation Space:** Box(-inf, inf, (73,), float32)
- Car state: position, velocity, rotation, boost, flags (33 dims)
- Ball state: position, velocity (6 dims)
- Boost pads: active status for all 34 pads (34 dims)

**Action Space:** Box([-1, -1, -1, -1, -1, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1], (8,), float32)
- Continuous: throttle, steer, pitch, yaw, roll
- Binary: jump, boost, handbrake

**Rewards:**
- Ball velocity toward opponent goal
- Bonus for touching ball (+0.1)
- Large bonus for scoring goal (+10.0)
- Large penalty for being scored on (-10.0)
- Penalty for being demoed (-1.0)

**Termination:** Goal scored  
**Truncation:** Time limit reached (default 300 seconds)

## Next Steps

- Modify reward function in `src/pettingzoo_env.py`
- Customize observation space (add more features)
- Implement curriculum learning (start with 1v1, progress to 3v3)
- Train with your favorite RL algorithm!
