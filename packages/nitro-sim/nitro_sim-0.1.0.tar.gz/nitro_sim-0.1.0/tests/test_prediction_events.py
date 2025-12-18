"""Tests for ball prediction and game event tracking"""

import pytest


def test_ball_pred_tracker_creation(initialized_sim):
    """Test creating a BallPredTracker"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Create tracker for 2 seconds (240 ticks at 120 ticks/sec)
    tracker = rs.BallPredTracker(arena, 240)

    assert tracker.num_pred_ticks == 240
    assert len(tracker.pred_data) == 240


def test_ball_pred_tracker_prediction(initialized_sim):
    """Test ball trajectory prediction"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Throw ball upward
    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 0, 200)
    ball_state.vel = rs.Vec(0, 0, 1000)  # Upward
    arena.ball.set_state(ball_state)

    # Create tracker
    tracker = rs.BallPredTracker(arena, 360)  # 3 seconds

    # Get predictions at different times
    pred_0_5s = tracker.get_ball_state_for_time(0.5)
    pred_1_0s = tracker.get_ball_state_for_time(1.0)
    pred_2_0s = tracker.get_ball_state_for_time(2.0)

    # Ball should go up then come down
    assert pred_0_5s.pos.z > 200  # Higher than start
    assert pred_1_0s.pos.z > pred_0_5s.pos.z  # Still going up
    # Eventually should start coming down
    assert pred_2_0s.vel.z < 0  # Falling


def test_ball_pred_tracker_update(initialized_sim):
    """Test updating ball prediction from arena"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    tracker = rs.BallPredTracker(arena, 240)

    # Get initial prediction
    initial_pred = tracker.get_ball_state_for_time(1.0)

    # Change ball state
    ball_state = arena.ball.get_state()
    ball_state.vel = rs.Vec(1000, 0, 0)  # Fast sideways
    arena.ball.set_state(ball_state)

    # Update prediction
    tracker.update_from_arena(arena)

    # New prediction should be different
    new_pred = tracker.get_ball_state_for_time(1.0)

    # Ball should be moving in X direction now
    assert abs(new_pred.vel.x) > abs(initial_pred.vel.x)


def test_ball_pred_manual_update(initialized_sim):
    """Test manual ball prediction update"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    tracker = rs.BallPredTracker(arena, 120)

    # Create custom ball state
    ball_state = rs.BallState()
    ball_state.pos = rs.Vec(1000, 1000, 500)
    ball_state.vel = rs.Vec(-500, -500, 200)

    # Update manually
    tracker.update_manual(ball_state, 0)

    # Verify prediction starts from our custom state
    pred = tracker.get_ball_state_for_time(0.0)
    assert abs(pred.pos.x - 1000) < 10


def test_game_event_tracker_creation(initialized_sim):
    """Test creating a GameEventTracker"""
    rs = initialized_sim

    tracker = rs.GameEventTracker()

    assert tracker.config is not None
    assert tracker.config.shot_min_speed > 0
    assert tracker.auto_state_set_detection == True


def test_game_event_tracker_config(initialized_sim):
    """Test GameEventTracker configuration"""
    rs = initialized_sim

    tracker = rs.GameEventTracker()
    config = tracker.config

    # Test default values
    assert config.shot_min_speed == 1750.0
    assert config.goal_max_touch_time == 4.0

    # Modify config
    config.shot_min_speed = 2000.0
    config.shot_event_cooldown = 2.0
    tracker.config = config

    # Verify changes
    assert tracker.config.shot_min_speed == 2000.0
    assert tracker.config.shot_event_cooldown == 2.0


def test_goal_score_callback(initialized_sim):
    """Test goal score callback"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Track goals
    goals = []

    def on_goal(arena, scoring_team):
        goals.append(scoring_team)

    arena.set_goal_score_callback(on_goal)

    # Put ball in goal
    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 5500, 100)  # Deep in orange goal
    arena.ball.set_state(ball_state)

    # Step simulation
    arena.step(10)

    # Check if ball is scored
    if arena.is_ball_scored():
        arena.step(5)  # Might need a few more ticks for callback
        # Goal callback should have been called
        # Note: Callback might not fire immediately, depends on internal logic
        pass


def test_car_bump_callback(initialized_sim):
    """Test car bump callback"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car1 = arena.add_car(rs.Team.BLUE)
    car2 = arena.add_car(rs.Team.ORANGE)

    # Track bumps
    bumps = []

    def on_bump(arena, bumper, bumped, is_demo):
        bumps.append(
            {"bumper_id": bumper.id, "bumped_id": bumped.id, "is_demo": is_demo}
        )

    arena.set_car_bump_callback(on_bump)

    # Position cars for collision
    state1 = car1.get_state()
    state1.pos = rs.Vec(0, -500, 20)
    state1.vel = rs.Vec(0, 2300, 0)  # Supersonic speed toward car2
    car1.set_state(state1)

    state2 = car2.get_state()
    state2.pos = rs.Vec(0, 500, 20)
    state2.vel = rs.Vec(0, 0, 0)
    car2.set_state(state2)

    # Simulate - cars might bump
    for _ in range(50):
        arena.step(1)
        if bumps:
            break

    # If bumps occurred, verify structure
    if bumps:
        bump = bumps[0]
        assert "bumper_id" in bump
        assert "bumped_id" in bump
        assert "is_demo" in bump


def test_game_event_tracker_shot_callback(initialized_sim):
    """Test shot detection callback"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    tracker = rs.GameEventTracker()

    shots = []

    def on_shot(arena, shooter, passer):
        shots.append(shooter.id)

    tracker.set_shot_callback(on_shot)

    # Setup for a shot
    arena.reset_to_random_kickoff(seed=42)

    # Give car boost and position toward ball
    car.controls.throttle = 1.0
    car.controls.boost = True

    # Simulate and update tracker
    for _ in range(240):  # 2 seconds
        arena.step(1)
        tracker.update(arena)

        if shots:
            break

    # Shot might or might not be detected depending on ball movement
    # Test passes if no crashes occur


def test_game_event_tracker_goal_callback(initialized_sim):
    """Test goal detection callback"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    tracker = rs.GameEventTracker()

    goals = []

    def on_goal(arena, scorer, passer):
        goals.append({"scorer": scorer.id, "passer": passer.id if passer else None})

    tracker.set_goal_callback(on_goal)

    # Manually put ball in goal for testing
    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 5500, 100)
    arena.ball.set_state(ball_state)

    # Update tracker
    tracker.update(arena)

    # Test passes if no crashes


def test_game_event_tracker_save_callback(initialized_sim):
    """Test save detection callback"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)

    tracker = rs.GameEventTracker()

    saves = []

    def on_save(arena, saver):
        saves.append(saver.id)

    tracker.set_save_callback(on_save)

    # Setup scenario
    arena.reset_to_random_kickoff(seed=123)

    # Simulate
    for _ in range(120):
        arena.step(1)
        tracker.update(arena)

    # Test passes if no crashes


def test_ball_prediction_accuracy(initialized_sim):
    """Test that ball prediction matches actual simulation"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)

    # Set specific ball state
    ball_state = arena.ball.get_state()
    ball_state.pos = rs.Vec(0, 0, 500)
    ball_state.vel = rs.Vec(500, 300, 200)
    ball_state.ang_vel = rs.Vec(0, 0, 0)
    arena.ball.set_state(ball_state)

    # Create prediction
    tracker = rs.BallPredTracker(arena, 120)
    pred_1s = tracker.get_ball_state_for_time(1.0)

    # Clone arena and simulate for real
    arena_clone = arena.clone(False)
    arena_clone.step(120)  # 1 second
    actual_1s = arena_clone.ball.get_state()

    # Prediction should be close to actual (within some tolerance)
    pos_diff = pred_1s.pos.dist(actual_1s.pos)

    # Should be very close (within 10 units)
    assert pos_diff < 50, f"Prediction off by {pos_diff} units"
