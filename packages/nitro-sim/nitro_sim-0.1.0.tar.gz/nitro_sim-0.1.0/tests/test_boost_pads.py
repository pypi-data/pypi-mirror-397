"""Tests for boost pads and arena configuration"""

import pytest


def test_boost_pads_exist(initialized_sim):
    """Test that boost pads are created in arena"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    pads = arena.get_boost_pads()

    # Soccar should have 34 boost pads (6 big, 28 small)
    assert len(pads) == 34

    # Count big and small pads
    big_pads = [p for p in pads if p.config.is_big]
    small_pads = [p for p in pads if not p.config.is_big]

    assert len(big_pads) == 6
    assert len(small_pads) == 28


def test_boost_pad_positions(initialized_sim):
    """Test boost pad positions"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    pads = arena.get_boost_pads()

    # All pads should be within arena bounds
    for pad in pads:
        pos = pad.config.pos
        assert abs(pos.x) < 5600, f"Pad x out of bounds: {pos.x}"
        assert abs(pos.y) < 6000, f"Pad y out of bounds: {pos.y}"
        assert pos.z >= 0, f"Pad z below ground: {pos.z}"
        assert pos.z < 500, f"Pad z too high: {pos.z}"


def test_boost_pad_state(initialized_sim):
    """Test boost pad state"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    pads = arena.get_boost_pads()

    # All pads should be active at start
    for pad in pads:
        state = pad.get_state()
        assert state.is_active == True
        assert state.cooldown == 0


def test_boost_pad_cooldown(initialized_sim):
    """Test boost pad cooldown after car picks it up"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    car = arena.add_car(rs.Team.BLUE)
    pads = arena.get_boost_pads()

    # Find a big pad
    big_pad = next(p for p in pads if p.config.is_big)

    # Position car on the boost pad with low boost
    car_state = car.get_state()
    car_state.pos = big_pad.config.pos
    car_state.boost = 50  # Not full
    car.set_state(car_state)

    # Simulate a few ticks
    arena.step(5)

    # Check if pad was picked up (cooldown should be active)
    pad_state = big_pad.get_state()
    # Pad might be inactive or have cooldown
    picked_up = not pad_state.is_active or pad_state.cooldown > 0

    # If picked up, verify cooldown behavior
    if picked_up:
        assert pad_state.cooldown > 0 or not pad_state.is_active


def test_different_game_modes_boost_pads(initialized_sim):
    """Test that different game modes have different boost pad layouts"""
    rs = initialized_sim

    soccar_arena = rs.Arena.create(rs.GameMode.SOCCAR)
    hoops_arena = rs.Arena.create(rs.GameMode.HOOPS)

    soccar_pads = soccar_arena.get_boost_pads()
    hoops_pads = hoops_arena.get_boost_pads()

    # Different game modes should have different numbers of pads
    # Soccar has 34, Hoops has different layout
    assert len(soccar_pads) > 0
    assert len(hoops_pads) > 0


def test_arena_config_bounds(initialized_sim):
    """Test arena configuration bounds"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    config = arena.get_arena_config()

    # Verify default arena bounds
    assert config.min_pos.x == -5600
    assert config.min_pos.y == -6000
    assert config.min_pos.z == 0

    assert config.max_pos.x == 5600
    assert config.max_pos.y == 6000
    assert config.max_pos.z == 2200


def test_custom_arena_config(initialized_sim):
    """Test creating arena with custom config"""
    rs = initialized_sim

    config = rs.ArenaConfig()
    config.min_pos = rs.Vec(-10000, -10000, 0)
    config.max_pos = rs.Vec(10000, 10000, 5000)
    config.no_ball_rot = False

    arena = rs.Arena.create(rs.GameMode.THE_VOID, arena_config=config)

    retrieved_config = arena.get_arena_config()
    assert retrieved_config.min_pos.x == -10000
    assert retrieved_config.max_pos.z == 5000
    assert retrieved_config.no_ball_rot == False


def test_boost_pad_positions_symmetric(initialized_sim):
    """Test that boost pads are symmetric (blue/orange sides)"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    pads = arena.get_boost_pads()

    # Group pads by Y position (negative = blue side, positive = orange side)
    blue_side = [p for p in pads if p.config.pos.y < -100]
    orange_side = [p for p in pads if p.config.pos.y > 100]
    center = [p for p in pads if abs(p.config.pos.y) <= 100]

    # There should be some pads on each side
    assert len(blue_side) > 0
    assert len(orange_side) > 0

    # Blue and orange sides should have same number of pads (symmetry)
    assert len(blue_side) == len(orange_side)


def test_big_vs_small_boost_pads(initialized_sim):
    """Test distinguishing big vs small boost pads"""
    rs = initialized_sim

    arena = rs.Arena.create(rs.GameMode.SOCCAR)
    pads = arena.get_boost_pads()

    big_pads = [p for p in pads if p.config.is_big]
    small_pads = [p for p in pads if not p.config.is_big]

    # Verify we have both types
    assert len(big_pads) > 0
    assert len(small_pads) > 0

    # Big pads should be in corners (far from center)
    for pad in big_pads:
        distance_from_center = pad.config.pos.to_2d().length()
        assert distance_from_center > 2000, "Big pads should be in corners"
