"""Integration tests for RocketSim simulation (requires collision meshes)"""

import pytest


def test_arena_creation_initialized(initialized_sim):
    """Test Arena creation after initialization"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    assert arena is not None
    assert arena.game_mode == rs.GameMode.SOCCAR
    assert arena.tick_count == 0
    assert arena.ball is not None


def test_car_addition(initialized_sim):
    """Test adding cars to arena"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Add blue team car
    car1 = arena.add_car(rs.Team.BLUE, rs.CAR_CONFIG_OCTANE)
    assert car1 is not None
    assert car1.team == rs.Team.BLUE
    assert car1.id > 0

    # Add orange team car
    car2 = arena.add_car(rs.Team.ORANGE, rs.CAR_CONFIG_DOMINUS)
    assert car2 is not None
    assert car2.team == rs.Team.ORANGE
    assert car2.id != car1.id

    # Check cars list
    cars = arena.get_cars()
    assert len(cars) == 2


def test_car_state(initialized_sim):
    """Test car state get/set"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Get initial state
    state = car.get_state()
    assert state.pos.z > 0  # Car should be spawned above ground
    assert state.is_on_ground == True
    assert state.boost >= 0

    # Modify state
    state.pos = rs.Vec(1000, 2000, 100)
    state.vel = rs.Vec(500, 0, 0)
    state.boost = 100

    # Set state
    car.set_state(state)

    # Verify state was set
    new_state = car.get_state()
    assert new_state.pos.x == 1000
    assert new_state.pos.y == 2000
    assert new_state.vel.x == 500
    assert new_state.boost == 100


def test_ball_state(initialized_sim):
    """Test ball state get/set"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Get initial ball state
    ball_state = arena.ball.get_state()
    assert ball_state.pos.z > 0  # Ball spawned above ground

    # Modify ball state
    ball_state.pos = rs.Vec(0, 0, 1000)
    ball_state.vel = rs.Vec(0, 0, 1000)

    # Set ball state
    arena.ball.set_state(ball_state)

    # Verify
    new_state = arena.ball.get_state()
    assert new_state.pos.z == 1000
    assert new_state.vel.z == 1000


def test_simulation_step(initialized_sim):
    """Test arena simulation stepping"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Set car controls
    car.controls.throttle = 1.0
    car.controls.boost = True

    initial_tick = arena.tick_count
    initial_state = car.get_state()

    # Step simulation
    arena.step(10)

    # Verify simulation advanced
    assert arena.tick_count == initial_tick + 10

    # Car should have moved
    new_state = car.get_state()
    # With throttle and boost, car should have velocity
    assert new_state.vel.length() > initial_state.vel.length()


def test_car_controls_effect(initialized_sim):
    """Test that car controls affect the car"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Reset to known state
    arena.reset_to_random_kickoff(seed=42)

    initial_state = car.get_state()

    # Apply boost
    car.controls.boost = True
    car.controls.throttle = 1.0

    # Simulate
    arena.step(120)  # 1 second at 120 ticks/sec

    final_state = car.get_state()

    # Car should have gained speed
    assert final_state.vel.length() > initial_state.vel.length()


def test_ball_physics(initialized_sim):
    """Test ball physics (gravity)"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Throw ball upward so we can watch gravity slow it down and reverse it
    ball_state = arena.ball.get_state()
    ball_state.vel = rs.Vec(0, 0, 1000)  # Throw upward
    ball_state.ang_vel = rs.Vec(0, 0, 0)
    arena.ball.set_state(ball_state)

    initial_vel_z = arena.ball.get_state().vel.z

    # Simulate - gravity should slow the ball down
    arena.step(60)  # 0.5 seconds
    mid_state = arena.ball.get_state()

    # Velocity should have decreased due to gravity
    assert mid_state.vel.z < initial_vel_z, "Gravity didn't slow the ball"

    # Simulate more - ball should eventually start falling
    arena.step(150)  # 1.25 more seconds (1.75 total)
    final_state = arena.ball.get_state()

    # Ball should now be falling (negative velocity)
    assert final_state.vel.z < 0, (
        f"Ball not falling after 1.75s: vel.z={final_state.vel.z}"
    )


def test_kickoff_reset(initialized_sim):
    """Test kickoff reset"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Mess up the arena state
    car_state = car.get_state()
    car_state.pos = rs.Vec(5000, 5000, 1000)
    car.set_state(car_state)

    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(1000, 1000, 1000)
    arena.ball.set_state(ball_state)

    # Reset to kickoff
    arena.reset_to_random_kickoff(seed=42)

    # Verify positions are reasonable for kickoff
    new_car_state = car.get_state()
    new_ball_state = arena.ball.get_state()

    # Ball should be near center
    assert abs(new_ball_state.pos.x) < 100
    assert abs(new_ball_state.pos.y) < 100

    # Car should be in a kickoff position
    assert abs(new_car_state.pos.x) < 5000
    assert abs(new_car_state.pos.y) < 6000


def test_different_car_configs(initialized_sim):
    """Test different car configurations"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    configs = [
        rs.CAR_CONFIG_OCTANE,
        rs.CAR_CONFIG_DOMINUS,
        rs.CAR_CONFIG_PLANK,
        rs.CAR_CONFIG_BREAKOUT,
        rs.CAR_CONFIG_HYBRID,
        rs.CAR_CONFIG_MERC,
    ]

    for config in configs:
        car = arena.add_car(rs.Team.BLUE, config)
        assert car is not None
        assert car.config.hitbox_size.length() > 0


def test_mutator_config(initialized_sim):
    """Test mutator configuration"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Get default mutator config
    mutators = arena.get_mutator_config()

    # Modify mutators
    mutators.boost_accel_ground = 5000.0  # Super boost on ground
    mutators.boost_accel_air = 4000.0  # Super boost in air
    mutators.ball_max_speed = 10000.0  # Fast ball

    arena.set_mutator_config(mutators)

    # Verify
    new_mutators = arena.get_mutator_config()
    assert new_mutators.boost_accel_ground == 5000.0
    assert new_mutators.boost_accel_air == 4000.0
    assert new_mutators.ball_max_speed == 10000.0


@pytest.mark.skip(reason="Arena clone has memory management issues during cleanup")
def test_arena_clone(initialized_sim):
    """Test arena cloning"""
    rs = initialized_sim

    arena1 = rs.Arena.create(rs.GameMode.SOCCAR)
    car1 = arena1.add_car(rs.Team.BLUE)

    # Set specific state
    car1_state = car1.get_state()
    car1_state.pos = rs.Vec(1234, 5678, 100)
    car1.set_state(car1_state)

    # Simulate a bit
    arena1.step(50)

    # Clone arena
    arena2 = arena1.clone(copy_callbacks=False)

    assert arena2 is not None
    assert arena2.tick_count == arena1.tick_count

    # Get cars from cloned arena
    cars2 = arena2.get_cars()
    assert len(cars2) == 1


def test_tick_rate(initialized_sim):
    """Test tick rate property"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR, tick_rate=60.0)

    assert abs(arena.tick_rate - 60.0) < 0.01

    # Change tick rate
    arena.tick_rate = 120.0
    assert abs(arena.tick_rate - 120.0) < 0.01
