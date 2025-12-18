"""Tests for RocketSim game types (GameMode, Team, etc.)"""

import pytest


def test_game_mode_enum():
    """Test GameMode enum values"""
    import nitro as rs

    assert hasattr(rs.GameMode, "SOCCAR")
    assert hasattr(rs.GameMode, "HOOPS")
    assert hasattr(rs.GameMode, "HEATSEEKER")
    assert hasattr(rs.GameMode, "SNOWDAY")
    assert hasattr(rs.GameMode, "DROPSHOT")
    assert hasattr(rs.GameMode, "THE_VOID")


def test_team_enum():
    """Test Team enum values"""
    import nitro as rs

    assert hasattr(rs.Team, "BLUE")
    assert hasattr(rs.Team, "ORANGE")


def test_car_controls():
    """Test CarControls initialization and fields"""
    import nitro as rs

    controls = rs.CarControls()

    # Test default values (should be zero)
    assert controls.throttle == 0
    assert controls.steer == 0
    assert controls.pitch == 0
    assert controls.yaw == 0
    assert controls.roll == 0
    assert controls.jump == False
    assert controls.boost == False
    assert controls.handbrake == False

    # Test setting values
    controls.throttle = 1.0
    controls.steer = 0.5
    controls.boost = True

    assert controls.throttle == 1.0
    assert controls.steer == 0.5
    assert controls.boost == True


def test_car_controls_clamp():
    """Test CarControls clamping"""
    import nitro as rs

    controls = rs.CarControls()

    # Set out of range values
    controls.throttle = 2.0
    controls.steer = -2.0
    controls.pitch = 5.0

    # Clamp to valid range
    controls.clamp_fix()

    assert controls.throttle == 1.0
    assert controls.steer == -1.0
    assert controls.pitch == 1.0


def test_phys_state():
    """Test PhysState initialization and fields"""
    import nitro as rs

    state = rs.PhysState()

    # Test default values
    assert state.pos.is_zero()
    assert state.vel.is_zero()
    assert state.ang_vel.is_zero()

    # Test setting values
    state.pos = rs.Vec(1000, 2000, 100)
    state.vel = rs.Vec(500, 0, 0)

    assert state.pos.x == 1000
    assert state.vel.x == 500


def test_ball_state():
    """Test BallState (inherits from PhysState)"""
    import nitro as rs

    state = rs.BallState()

    # Should have PhysState fields
    assert hasattr(state, "pos")
    assert hasattr(state, "vel")
    assert hasattr(state, "ang_vel")
    assert hasattr(state, "rot_mat")


def test_car_state():
    """Test CarState initialization and fields"""
    import nitro as rs

    state = rs.CarState()

    # Test PhysState inheritance
    assert hasattr(state, "pos")
    assert hasattr(state, "vel")

    # Test CarState specific fields
    assert state.is_on_ground == True
    assert state.has_jumped == False
    assert state.has_double_jumped == False
    assert state.has_flipped == False
    assert state.boost >= 0 and state.boost <= 100
    assert state.is_supersonic == False
    assert state.is_demoed == False


def test_car_state_methods():
    """Test CarState methods"""
    import nitro as rs

    state = rs.CarState()

    # Initially should have flip or jump
    assert state.has_flip_or_jump() == True

    # Initially should not have flip reset
    assert state.has_flip_reset() == False
    assert state.got_flip_reset() == False


def test_ball_hit_info():
    """Test BallHitInfo"""
    import nitro as rs

    info = rs.BallHitInfo()

    assert hasattr(info, "is_valid")
    assert hasattr(info, "relative_pos_on_ball")
    assert hasattr(info, "ball_pos")
    assert hasattr(info, "extra_hit_vel")
