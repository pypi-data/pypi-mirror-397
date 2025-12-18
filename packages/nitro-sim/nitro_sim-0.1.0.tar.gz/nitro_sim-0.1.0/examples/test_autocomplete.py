"""Test file to demonstrate LSP autocomplete support"""

import nitro as rs

# Create a vector - you should get autocomplete for x, y, z
v = rs.Vec(1, 2, 3)

# Autocomplete should show all Vec methods
print(v.length())  # Autocomplete: length, length_2d, length_sq, etc.
print(v.normalized())
print(v.dot(rs.Vec(0, 1, 0)))

# Autocomplete for GameMode enum
mode = rs.GameMode.SOCCAR  # Should show: SOCCAR, HOOPS, HEATSEEKER, etc.

# Autocomplete for CarControls
controls = rs.CarControls()
controls.throttle = (
    1.0  # Should show: throttle, steer, pitch, yaw, roll, jump, boost, handbrake
)
controls.boost = True

# Autocomplete for preset configs
config = rs.CAR_CONFIG_OCTANE  # Should show all CAR_CONFIG_* presets


# Type checking should work
def process_vector(vec: rs.Vec) -> float:
    """Type hints work for better IDE support"""
    return vec.length()


result = process_vector(v)
print(f"Vector length: {result}")

# Autocomplete for Arena (when initialized)
# arena = rs.Arena.create(rs.GameMode.SOCCAR)
# arena.  # Should show: step, add_car, get_cars, ball, tick_count, etc.
