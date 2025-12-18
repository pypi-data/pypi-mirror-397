"""Pytest configuration and fixtures for RocketSim tests"""

import pytest
import os
import zipfile
import urllib.request
import ssl
from pathlib import Path


# Get collision meshes URL from environment variable or use default
COLLISION_MESHES_URL = os.environ.get(
    "ROCKETSIM_COLLISION_MESHES_URL",
    "https://pub-1156019cab034572bdd5ea3bc9f51ee2.r2.dev/collision_meshes.zip",
)
COLLISION_MESHES_DIR = Path(__file__).parent.parent / "collision_meshes"


def download_collision_meshes():
    """Download and extract collision meshes if not present"""
    if COLLISION_MESHES_DIR.exists():
        return True

    print(f"\nDownloading collision meshes from {COLLISION_MESHES_URL}...")

    try:
        # Create temp directory for download
        COLLISION_MESHES_DIR.parent.mkdir(parents=True, exist_ok=True)
        zip_path = COLLISION_MESHES_DIR.parent / "collision_meshes.zip"

        # Create SSL context that doesn't verify certificates (for R2 public buckets)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Create request with user agent (some CDNs require it)
        req = urllib.request.Request(
            COLLISION_MESHES_URL,
            headers={"User-Agent": "Mozilla/5.0 (Python; RocketSim Test Suite)"},
        )

        # Download the zip file
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_context)
        )
        with opener.open(req) as response, open(zip_path, "wb") as out_file:
            out_file.write(response.read())

        print(f"Extracting collision meshes to {COLLISION_MESHES_DIR}...")

        # Create the collision_meshes directory
        COLLISION_MESHES_DIR.mkdir(parents=True, exist_ok=True)

        # Extract the zip file directly into collision_meshes directory
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(COLLISION_MESHES_DIR)

        # Clean up zip file
        zip_path.unlink()

        # Verify that game mode folders exist
        expected_folders = ["soccar", "hoops", "dropshot"]
        if any((COLLISION_MESHES_DIR / folder).exists() for folder in expected_folders):
            print(f"✓ Collision meshes ready at {COLLISION_MESHES_DIR}")
            return True
        else:
            print(f"✗ Extraction failed - no game mode folders found")
            return False

    except Exception as e:
        print(f"✗ Failed to download collision meshes: {e}")
        return False


@pytest.fixture(scope="session")
def collision_meshes_path():
    """Fixture that provides path to collision meshes, downloading if needed

    Can be configured via environment variables:
    - ROCKETSIM_COLLISION_MESHES_PATH: Use existing collision meshes at this path
    - ROCKETSIM_COLLISION_MESHES_URL: Download from this URL if not found locally
    """
    # Check if user specified an existing path
    env_path = os.environ.get("ROCKETSIM_COLLISION_MESHES_PATH")
    if env_path and Path(env_path).exists():
        print(f"\n✓ Using collision meshes from: {env_path}")
        return env_path

    # Try to download if not present
    if not download_collision_meshes():
        pytest.skip(
            "Collision meshes not available. "
            "Set ROCKETSIM_COLLISION_MESHES_PATH or ROCKETSIM_COLLISION_MESHES_URL environment variable."
        )

    return str(COLLISION_MESHES_DIR)


@pytest.fixture(scope="session")
def initialized_sim(collision_meshes_path):
    """Fixture that initializes RocketSim once for all tests"""
    import nitro as rs

    # Initialize RocketSim
    rs.init(collision_meshes_path, silent=True)

    # Verify initialization
    assert rs.get_stage() == rs.RocketSimStage.INITIALIZED

    return rs
