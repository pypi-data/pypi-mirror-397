# RocketSim Python Bindings Tests

## Test Organization

- **test_math_types.py** - Math operations (Vec, RotMat, Angle) - no collision meshes needed
- **test_game_types.py** - Game types and data structures - no collision meshes needed  
- **test_arena.py** - Arena configuration and interfaces - no collision meshes needed
- **test_simulation.py** - Single car and ball simulation tests - **requires collision meshes**
- **test_multi_vehicle.py** - Multiple cars and ball interactions - **requires collision meshes**
- **test_boost_pads.py** - Boost pad positions, states, and arena bounds - **requires collision meshes**
- **test_prediction_events.py** - Ball prediction and game event tracking - **requires collision meshes**

## Running Tests

### Quick Tests (No Collision Meshes)

Run tests that don't require collision meshes:

```bash
uv run pytest tests/ -k "not simulation" -v
```

### Full Tests (With Collision Meshes)

You have several options to provide collision meshes:

#### Option 1: Use Environment Variable (Recommended)

If you already have collision meshes downloaded:

```bash
export ROCKETSIM_COLLISION_MESHES_PATH=/path/to/collision_meshes
uv run pytest tests/ -v
```

#### Option 2: Auto-Download from Custom URL

If you have the collision meshes hosted at a public URL:

```bash
export ROCKETSIM_COLLISION_MESHES_URL=https://your-url.com/collision_meshes.zip
uv run pytest tests/ -v
```

The tests will automatically download and extract the meshes to `./collision_meshes/` (which is gitignored).

#### Option 3: Manual Download

1. Download `collision_meshes.zip` from your source
2. Extract to project root as `collision_meshes/`
3. Run tests:

```bash
uv run pytest tests/ -v
```

## Collision Meshes Location

The collision meshes can be obtained from:
- The official RocketSim repository
- Your R2 bucket (requires authentication or public URL)
- Any other source that has the standard RocketSim collision mesh format

The tests will look for meshes in this order:
1. `ROCKETSIM_COLLISION_MESHES_PATH` environment variable
2. Auto-download from `ROCKETSIM_COLLISION_MESHES_URL` 
3. Local `./collision_meshes/` directory

## Current Test Status

```bash
$ uv run pytest tests/
================= 72 passed, 2 skipped in 1.55s =================
```

**Without collision meshes:** 30 tests pass, 1 skipped
**With collision meshes (auto-downloaded):** 72 tests pass, 2 skipped

### Test Breakdown:
- **Math types** (14 tests): Vec, RotMat, Angle operations
- **Game types** (9 tests): Enums, controls, states, configs
- **Arena config** (7 tests): Configuration and interface tests
- **Simulation** (11 tests): Single car, ball physics, mutators
- **Multi-vehicle** (10 tests): Multiple cars, ball interactions, 3v3 games
- **Boost pads** (9 tests): Boost pad positions, states, arena bounds, symmetry
- **Prediction & Events** (12 tests): Ball prediction, event tracking, callbacks

### Skipped Tests:
- `test_arena_creation` - Requires manual RocketSim initialization (not needed with fixtures)
- `test_arena_clone` - Arena cloning has memory management issues during cleanup

## CI/CD Integration

For CI/CD pipelines, you can either:

1. Store collision meshes as a CI artifact/cache
2. Use a secret environment variable with a download URL
3. Skip simulation tests in CI if meshes aren't available

Example GitHub Actions:

```yaml
- name: Run tests
  env:
    ROCKETSIM_COLLISION_MESHES_URL: ${{ secrets.COLLISION_MESHES_URL }}
  run: uv run pytest tests/ -v
```
