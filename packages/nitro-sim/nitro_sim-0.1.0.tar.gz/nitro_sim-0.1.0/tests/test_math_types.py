"""Tests for RocketSim math types (Vec, RotMat, Angle)"""

import pytest
import math


def test_vec_construction():
    """Test Vec construction and basic properties"""
    import nitro as rs

    # Default constructor
    v1 = rs.Vec()
    assert v1.x == 0 and v1.y == 0 and v1.z == 0
    assert v1.is_zero()

    # Constructor with values
    v2 = rs.Vec(1, 2, 3)
    assert v2.x == 1 and v2.y == 2 and v2.z == 3
    assert not v2.is_zero()


def test_vec_operations():
    """Test Vec mathematical operations"""
    import nitro as rs

    v1 = rs.Vec(1, 2, 3)
    v2 = rs.Vec(4, 5, 6)

    # Addition
    v3 = v1 + v2
    assert v3.x == 5 and v3.y == 7 and v3.z == 9

    # Subtraction
    v4 = v2 - v1
    assert v4.x == 3 and v4.y == 3 and v4.z == 3

    # Scalar multiplication
    v5 = v1 * 2
    assert v5.x == 2 and v5.y == 4 and v5.z == 6

    # Scalar division
    v6 = v2 / 2
    assert v6.x == 2 and v6.y == 2.5 and v6.z == 3

    # Negation
    v7 = -v1
    assert v7.x == -1 and v7.y == -2 and v7.z == -3


def test_vec_length():
    """Test Vec length calculations"""
    import nitro as rs

    v = rs.Vec(3, 4, 0)
    assert v.length() == 5.0
    assert v.length_sq() == 25.0
    assert v.length_2d() == 5.0
    assert v.length_sq_2d() == 25.0

    v2 = rs.Vec(1, 0, 0)
    assert v2.length() == 1.0


def test_vec_dot_cross():
    """Test Vec dot and cross products"""
    import nitro as rs

    v1 = rs.Vec(1, 0, 0)
    v2 = rs.Vec(0, 1, 0)

    # Dot product (perpendicular vectors)
    assert v1.dot(v2) == 0

    # Cross product (perpendicular vectors)
    v3 = v1.cross(v2)
    assert v3.x == 0 and v3.y == 0 and v3.z == 1


def test_vec_normalized():
    """Test Vec normalization"""
    import nitro as rs

    v = rs.Vec(3, 4, 0)
    vn = v.normalized()
    assert abs(vn.length() - 1.0) < 1e-6
    assert abs(vn.x - 0.6) < 1e-6
    assert abs(vn.y - 0.8) < 1e-6


def test_vec_distance():
    """Test Vec distance calculations"""
    import nitro as rs

    v1 = rs.Vec(0, 0, 0)
    v2 = rs.Vec(3, 4, 0)

    assert v1.dist(v2) == 5.0
    assert v1.dist_sq(v2) == 25.0
    assert v1.dist_2d(v2) == 5.0
    assert v1.dist_sq_2d(v2) == 25.0


def test_vec_indexing():
    """Test Vec indexing"""
    import nitro as rs

    v = rs.Vec(1, 2, 3)
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3

    v[0] = 10
    assert v.x == 10


def test_rotmat_construction():
    """Test RotMat construction"""
    import nitro as rs

    # Default constructor
    r1 = rs.RotMat()
    assert r1.forward.is_zero()

    # Identity matrix
    r2 = rs.RotMat.get_identity()
    assert r2.forward.x == 1 and r2.forward.y == 0 and r2.forward.z == 0
    assert r2.right.x == 0 and r2.right.y == 1 and r2.right.z == 0
    assert r2.up.x == 0 and r2.up.y == 0 and r2.up.z == 1


def test_rotmat_look_at():
    """Test RotMat look_at function"""
    import nitro as rs

    forward = rs.Vec(1, 0, 0)
    up = rs.Vec(0, 0, 1)

    r = rs.RotMat.look_at(forward, up)
    assert abs(r.forward.normalized().x - 1.0) < 1e-6


def test_angle_construction():
    """Test Angle construction"""
    import nitro as rs

    # Default constructor
    a1 = rs.Angle()
    assert a1.yaw == 0 and a1.pitch == 0 and a1.roll == 0

    # Constructor with values
    a2 = rs.Angle(1.0, 0.5, -0.5)
    assert a2.yaw == 1.0
    assert a2.pitch == 0.5
    assert a2.roll == -0.5


def test_angle_conversion():
    """Test Angle to/from RotMat conversion"""
    import nitro as rs

    a = rs.Angle(0.0, 0.0, 0.0)
    r = a.to_rot_mat()
    a2 = rs.Angle.from_rot_mat(r)

    # Should be approximately the same
    assert abs(a2.yaw - a.yaw) < 1e-6
    assert abs(a2.pitch - a.pitch) < 1e-6
    assert abs(a2.roll - a.roll) < 1e-6


def test_angle_forward_vec():
    """Test Angle forward vector"""
    import nitro as rs

    # Looking forward (0 yaw, 0 pitch)
    a = rs.Angle(0, 0, 0)
    v = a.get_forward_vec()
    assert abs(v.x - 1.0) < 1e-6
    assert abs(v.y) < 1e-6


def test_angle_normalize():
    """Test Angle normalization"""
    import nitro as rs

    # Test angle wrapping
    a = rs.Angle(2 * math.pi + 0.5, 0, 0)
    a.normalize_fix()
    assert abs(a.yaw - 0.5) < 1e-6


def test_angle_indexing():
    """Test Angle indexing"""
    import nitro as rs

    a = rs.Angle(1, 2, 3)
    assert a[0] == 1  # yaw
    assert a[1] == 2  # pitch
    assert a[2] == 3  # roll

    a[0] = 5
    assert a.yaw == 5
