"""Tests for RocketSim Arena and simulation"""

import pytest


def test_car_config():
    """Test CarConfig and preset configs"""
    import nitro as rs

    config = rs.CarConfig()
    assert hasattr(config, "hitbox_size")
    assert hasattr(config, "hitbox_pos_offset")

    # Test preset configs exist
    assert hasattr(rs, "CAR_CONFIG_OCTANE")
    assert hasattr(rs, "CAR_CONFIG_DOMINUS")
    assert hasattr(rs, "CAR_CONFIG_PLANK")
    assert hasattr(rs, "CAR_CONFIG_BREAKOUT")
    assert hasattr(rs, "CAR_CONFIG_HYBRID")
    assert hasattr(rs, "CAR_CONFIG_MERC")


def test_mutator_config():
    """Test MutatorConfig"""
    import nitro as rs

    config = rs.MutatorConfig(rs.GameMode.SOCCAR)

    # Test some fields
    assert hasattr(config, "car_mass")
    assert hasattr(config, "ball_mass")
    assert hasattr(config, "boost_accel_ground")
    assert hasattr(config, "boost_accel_air")
    assert hasattr(config, "jump_accel")
    assert hasattr(config, "unlimited_flips")
    assert hasattr(config, "unlimited_double_jumps")

    # Test setting values
    config.car_mass = 200.0
    assert config.car_mass == 200.0


def test_arena_config():
    """Test ArenaConfig"""
    import nitro as rs

    config = rs.ArenaConfig()

    assert hasattr(config, "min_pos")
    assert hasattr(config, "max_pos")
    assert hasattr(config, "max_aabb_len")
    assert hasattr(config, "no_ball_rot")


@pytest.mark.skip(reason="Requires RocketSim initialization with collision meshes")
def test_arena_creation():
    """Test Arena creation (without initialization)"""
    import nitro as rs

    # Note: This test will likely fail without RocketSim.Init() being called
    # but we're testing the interface is available
    try:
        arena = rs.Arena.create(rs.GameMode.SOCCAR)

        # If it succeeds, test basic properties
        assert arena.game_mode == rs.GameMode.SOCCAR
        assert arena.tick_count == 0
        assert arena.ball is not None

    except RuntimeError as e:
        # Expected if RocketSim not initialized
        assert "ROCKETSIM" in str(e).upper() or "INIT" in str(e).upper()


def test_car_interface():
    """Test Car class interface (without creating real car)"""
    import nitro as rs

    # Just verify the class exists and has the right structure
    assert hasattr(rs, "Car")


def test_ball_interface():
    """Test Ball class interface"""
    import nitro as rs

    # Just verify the class exists and has the right structure
    assert hasattr(rs, "Ball")


def test_initialization_interface():
    """Test initialization function interface"""
    import nitro as rs

    # Test that init function exists
    assert hasattr(rs, "init")
    assert hasattr(rs, "get_stage")

    # Test RocketSimStage enum
    assert hasattr(rs.RocketSimStage, "UNINITIALIZED")
    assert hasattr(rs.RocketSimStage, "INITIALIZING")
    assert hasattr(rs.RocketSimStage, "INITIALIZED")

    # Get current stage
    stage = rs.get_stage()
    assert stage in [
        rs.RocketSimStage.UNINITIALIZED,
        rs.RocketSimStage.INITIALIZING,
        rs.RocketSimStage.INITIALIZED,
    ]


def test_version():
    """Test that version is exposed"""
    import nitro as rs

    assert hasattr(rs, "__version__")
    assert isinstance(rs.__version__, str)
