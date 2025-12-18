# Building nitro-sim

Complete guide for building and installing the RocketSim Python bindings.

## Prerequisites

You need:
- **Python 3.12+**
- **CMake 3.15+**
- **C++ compiler** with C++20 support
- **pybind11** (automatically installed)

## Quick Start

### Option 1: Development Install (Recommended)

For development, install in editable mode with `uv`:

```bash
# Install in editable mode
uv sync

# The package is now installed and ready to use
uv run python -c "import nitro as rs; print('Version:', rs.__version__)"
```

### Option 2: Regular Install

Install the package normally:

```bash
# Using uv
uv pip install .

# Or using pip
pip install .
```

### Option 3: Build Wheel

Build a wheel for distribution:

```bash
# Using uv
uv build

# Or using pip/build
pip install build
python -m build

# Wheels will be in dist/
ls dist/
# nitro-0.1.0-cp312-cp312-macosx_26_0_arm64.whl
# nitro-0.1.0.tar.gz
```

## Install from Wheel

```bash
# Install the built wheel
pip install dist/nitro-0.1.0-*.whl
```

## Development Workflow

```bash
# 1. Install in editable mode
uv sync

# 2. Make changes to C++ code in src/bindings.cpp

# 3. Rebuild (automatically happens on import)
uv pip install -e . --force-reinstall --no-deps

# 4. Test your changes
uv run pytest tests/

# 5. Or use Python directly
uv run python
>>> import nitro as rs
>>> rs.init("collision_meshes")
>>> arena = rs.Arena.create(rs.GameMode.SOCCAR)
```

## Troubleshooting

### "CMake not found"

Install CMake:

```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get install cmake

# Windows
choco install cmake
```

### "pybind11 not found"

This should be automatically installed, but if not:

```bash
pip install pybind11
```

### "Compiler not found"

Install a C++ compiler:

```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install build-essential

# Windows
# Install Visual Studio with C++ support
```

### Build fails with C++ errors

Make sure you have C++20 support:
- GCC 10+
- Clang 10+
- MSVC 2019+

### "collision_meshes not found" when running tests

The tests auto-download collision meshes, but you can also:

```bash
# Set environment variable to existing meshes
export ROCKETSIM_COLLISION_MESHES_PATH=/path/to/collision_meshes

# Or download manually
curl -L https://pub-1156019cab034572bdd5ea3bc9f51ee2.r2.dev/collision_meshes.zip -o collision_meshes.zip
unzip collision_meshes.zip -d collision_meshes
```

## Clean Build

To do a completely clean build:

```bash
# Remove build artifacts
rm -rf build/ dist/ *.egg-info .venv

# Reinstall from scratch
uv sync
```

## Verify Installation

```bash
# Check that the module loads
uv run python -c "import nitro; print(nitro.__version__)"

# Check that types work (LSP/autocomplete)
uv run python -c "
import nitro as rs
v = rs.Vec(1, 2, 3)
print(f'Vector length: {v.length()}')
"

# Run tests
uv run pytest tests/ -v
```

## Platform-Specific Notes

### macOS
- Works on both Intel (x86_64) and Apple Silicon (arm64)
- Requires Xcode Command Line Tools
- No additional configuration needed

### Linux
- Requires GCC 10+ or Clang 10+
- Install development packages: `build-essential`, `cmake`
- May need to install Python dev headers: `python3-dev`

### Windows
- Requires Visual Studio 2019+ with C++ support
- CMake and pybind11 via pip
- Use "x64 Native Tools Command Prompt" for building

## Building for Distribution

To create wheels for multiple Python versions:

```bash
# Install build tools
pip install build cibuildwheel

# Build wheels for current platform
cibuildwheel --platform auto

# Or use GitHub Actions (see .github/workflows/build.yml)
```

## What Gets Built

The build process:
1. Compiles RocketSim C++ library (static)
2. Compiles Python bindings (src/bindings.cpp)
3. Links everything into a Python extension module
4. Installs type stubs (nitro.pyi) for IDE support
5. Creates importable module: `nitro.cpython-312-darwin.so`

## Build Output

After building, you'll have:
- `nitro.cpython-*.so` (or `.pyd` on Windows) - The compiled extension
- `nitro.pyi` - Type stubs for autocomplete/type checking
- Built wheels in `dist/` (if using `uv build`)

## Next Steps

After building:
1. See [BINDINGS_README.md](BINDINGS_README.md) for API documentation
2. See [tests/README.md](tests/README.md) for running tests
3. See [test_autocomplete.py](test_autocomplete.py) for usage examples
