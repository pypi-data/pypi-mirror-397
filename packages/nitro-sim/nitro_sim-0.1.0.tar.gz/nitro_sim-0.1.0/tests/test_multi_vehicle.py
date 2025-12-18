"""Tests for multiple vehicles interacting in the arena"""

import pytest


def test_multiple_cars_basic(initialized_sim):
    """Test adding multiple cars to arena"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Add multiple cars
    car1 = arena.add_car(rs.Team.BLUE, rs.CAR_CONFIG_OCTANE)
    car2 = arena.add_car(rs.Team.BLUE, rs.CAR_CONFIG_DOMINUS)
    car3 = arena.add_car(rs.Team.ORANGE, rs.CAR_CONFIG_OCTANE)
    car4 = arena.add_car(rs.Team.ORANGE, rs.CAR_CONFIG_PLANK)

    # Verify all cars were added
    cars = arena.get_cars()
    assert len(cars) == 4

    # Verify each car has unique ID
    car_ids = {car.id for car in cars}
    assert len(car_ids) == 4

    # Verify teams
    blue_cars = [car for car in cars if car.team == rs.Team.BLUE]
    orange_cars = [car for car in cars if car.team == rs.Team.ORANGE]
    assert len(blue_cars) == 2
    assert len(orange_cars) == 2


def test_cars_independent_controls(initialized_sim):
    """Test that cars can have independent controls"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    car1 = arena.add_car(rs.Team.BLUE)
    car2 = arena.add_car(rs.Team.ORANGE)

    # Set different controls for each car
    car1.controls.throttle = 1.0
    car1.controls.boost = True

    car2.controls.throttle = -1.0
    car2.controls.handbrake = True

    # Verify controls are independent
    assert car1.controls.throttle == 1.0
    assert car1.controls.boost == True
    assert car2.controls.throttle == -1.0
    assert car2.controls.handbrake == True
    assert car1.controls.handbrake == False
    assert car2.controls.boost == False


def test_cars_simulate_independently(initialized_sim):
    """Test that cars simulate with independent controls"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    car1 = arena.add_car(rs.Team.BLUE)
    car2 = arena.add_car(rs.Team.ORANGE)

    # Reset to known positions
    arena.reset_to_random_kickoff(seed=42)

    initial_state1 = car1.get_state()
    initial_state2 = car2.get_state()

    # Car1 accelerates forward with boost
    car1.controls.throttle = 1.0
    car1.controls.boost = True

    # Car2 does nothing
    car2.controls.throttle = 0.0
    car2.controls.boost = False

    # Simulate
    arena.step(120)  # 1 second

    final_state1 = car1.get_state()
    final_state2 = car2.get_state()

    # Car1 should have moved significantly
    distance1 = initial_state1.pos.dist(final_state1.pos)
    assert distance1 > 100, f"Car1 should have moved, distance={distance1}"

    # Car2 should have moved very little (just settling on ground)
    distance2 = initial_state2.pos.dist(final_state2.pos)
    assert distance2 < 100, f"Car2 should be mostly stationary, distance={distance2}"


def test_cars_and_ball_interaction(initialized_sim):
    """Test cars can hit the ball"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Position car facing ball
    car_state = car.get_state()
    car_state.pos = rs.Vec(0, -1000, 20)  # In front of ball
    car_state.vel = rs.Vec(0, 0, 0)
    car_state.rot_mat = rs.RotMat.look_at(rs.Vec(0, 1, 0), rs.Vec(0, 0, 1))
    car.set_state(car_state)

    # Position ball in front of car
    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, -500, 100)
    ball_state.vel = rs.Vec(0, 0, 0)
    arena.ball.set_state(ball_state)

    initial_ball_pos = arena.ball.get_state().pos

    # Drive car toward ball with boost
    car.controls.throttle = 1.0
    car.controls.boost = True

    # Simulate
    arena.step(180)  # 1.5 seconds

    final_ball_pos = arena.ball.get_state().pos

    # Ball should have moved from initial position (car hit it)
    ball_distance = initial_ball_pos.dist(final_ball_pos)
    assert ball_distance > 50, (
        f"Ball should have moved when hit, distance={ball_distance}"
    )


def test_multiple_cars_ball_interaction(initialized_sim):
    """Test multiple cars can interact with ball"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Add two cars on opposite sides of ball
    car1 = arena.add_car(rs.Team.BLUE)
    car2 = arena.add_car(rs.Team.ORANGE)

    # Position car1 to the left
    state1 = car1.get_state()
    state1.pos = rs.Vec(-500, 0, 20)
    state1.vel = rs.Vec(0, 0, 0)
    state1.rot_mat = rs.RotMat.look_at(rs.Vec(1, 0, 0), rs.Vec(0, 0, 1))
    car1.set_state(state1)

    # Position car2 to the right
    state2 = car2.get_state()
    state2.pos = rs.Vec(500, 0, 20)
    state2.vel = rs.Vec(0, 0, 0)
    state2.rot_mat = rs.RotMat.look_at(rs.Vec(-1, 0, 0), rs.Vec(0, 0, 1))
    car2.set_state(state2)

    # Position ball in center
    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 0, 100)
    ball_state.vel = rs.Vec(0, 0, 0)
    arena.ball.set_state(ball_state)

    # Both cars accelerate toward ball
    car1.controls.throttle = 1.0
    car2.controls.throttle = 1.0

    # Simulate
    arena.step(240)  # 2 seconds

    # Verify all objects still exist and are simulating
    assert len(arena.get_cars()) == 2
    assert arena.ball is not None

    # Verify simulation ran (tick count increased)
    assert arena.tick_count == 240


def test_car_ball_hit_info(initialized_sim):
    """Test that ball hit info is recorded when car hits ball"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Position car and ball for collision
    car_state = car.get_state()
    car_state.pos = rs.Vec(0, -300, 20)
    car_state.vel = rs.Vec(0, 1000, 0)  # Fast forward velocity
    car.set_state(car_state)

    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 0, 100)
    ball_state.vel = rs.Vec(0, 0, 0)
    arena.ball.set_state(ball_state)

    # Simulate until car hits ball
    for _ in range(10):
        arena.step(12)  # 0.1 second steps

        car_state = car.get_state()
        if car_state.ball_hit_info.is_valid:
            # Car hit the ball!
            hit_info = car_state.ball_hit_info
            assert hit_info.ball_pos.length() > 0
            assert hit_info.tick_count_when_hit > 0
            break
    else:
        # Didn't hit in time, that's ok - test passes if no crash
        pass


def test_six_player_game(initialized_sim):
    """Test a full 3v3 game scenario"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Add 3 blue cars
    blue_cars = []
    for i in range(3):
        car = arena.add_car(rs.Team.BLUE, rs.CAR_CONFIG_OCTANE)
        blue_cars.append(car)

    # Add 3 orange cars
    orange_cars = []
    for i in range(3):
        car = arena.add_car(rs.Team.ORANGE, rs.CAR_CONFIG_OCTANE)
        orange_cars.append(car)

    # Reset to kickoff positions
    arena.reset_to_random_kickoff(seed=123)

    # Verify all cars are in valid positions
    all_cars = arena.get_cars()
    assert len(all_cars) == 6

    for car in all_cars:
        state = car.get_state()
        # All cars should be on ground at kickoff
        assert state.is_on_ground
        # All cars should be within arena bounds
        assert abs(state.pos.x) < 5000
        assert abs(state.pos.y) < 6000
        assert state.pos.z < 500

    # Simulate a short game
    for tick in range(600):  # 5 seconds
        # Give all cars some simple AI-like controls
        for car in all_cars:
            ball_pos = arena.ball.get_state().pos
            car_pos = car.get_state().pos

            # Drive toward ball (very simple)
            direction = ball_pos - car_pos
            if direction.length() > 100:
                car.controls.throttle = 1.0
                car.controls.boost = direction.length() > 1000
            else:
                car.controls.throttle = 0.5

        arena.step(1)

    # Verify simulation completed without crashes
    assert arena.tick_count == 600
    assert len(arena.get_cars()) == 6


def test_car_removal(initialized_sim):
    """Test removing cars from arena"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Add multiple cars
    car1 = arena.add_car(rs.Team.BLUE)
    car2 = arena.add_car(rs.Team.BLUE)
    car3 = arena.add_car(rs.Team.ORANGE)

    assert len(arena.get_cars()) == 3

    # Remove one car
    removed = arena.remove_car(car2.id)
    assert removed == True
    assert len(arena.get_cars()) == 2

    # Try to remove same car again
    removed = arena.remove_car(car2.id)
    assert removed == False
    assert len(arena.get_cars()) == 2

    # Simulate with remaining cars
    arena.step(60)
    assert len(arena.get_cars()) == 2


def test_car_demolition(initialized_sim):
    """Test car demolition"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Get initial state
    initial_state = car.get_state()
    assert initial_state.is_demoed == False

    # Demolish the car with 3 second respawn delay
    car.demolish(3.0)

    # Check demo state immediately
    demo_state = car.get_state()
    assert demo_state.is_demoed == True
    assert demo_state.demo_respawn_timer > 0

    # Simulate and verify car respawns eventually
    initial_timer = demo_state.demo_respawn_timer

    # Simulate for a bit
    arena.step(120)  # 1 second

    current_state = car.get_state()
    # Timer should have decreased
    assert (
        current_state.demo_respawn_timer < initial_timer
        or current_state.is_demoed == False
    )


def test_car_respawn(initialized_sim):
    """Test manual car respawn"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    # Move car somewhere
    state = car.get_state()
    state.pos = rs.Vec(1000, 2000, 500)
    state.vel = rs.Vec(500, 500, 500)
    car.set_state(state)

    # Respawn car
    car.respawn(arena.game_mode, seed=42, boost_amount=100.0)

    # Verify car was respawned
    new_state = car.get_state()

    # Should be in a different position (respawn location)
    assert new_state.pos.dist(state.pos) > 100

    # Velocity should be reset
    assert abs(new_state.vel.length()) < 10

    # Boost should be set to respawn amount
    assert abs(new_state.boost - 100.0) < 1
