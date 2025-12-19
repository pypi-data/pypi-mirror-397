"""Access package resources: data files and platform-specific binaries."""

import platform
from pathlib import Path

try:
    from importlib.resources import files
except ImportError:
    # Python < 3.9 fallback
    from importlib_resources import files


def get_data_file(filename: str) -> Path:
    """
    Get path to a data file in the dwf_sim.data package.
    
    Args:
        filename: Name of the data file (e.g., "AccFreqL150R1.txt")
        
    Returns:
        Path to the data file
    """
    data_package = files("dwf_sim.data")
    file_ref = data_package / filename
    return Path(str(file_ref))


def get_ngsngs_binary() -> Path:
    """
    Get path to the platform-specific NGSNGS binary.
    
    Returns:
        Path to the NGSNGS executable for the current platform
        
    Raises:
        RuntimeError: If the current platform is not supported
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map platform identifiers
    if system == "linux":
        if machine in ("x86_64", "amd64"):
            platform_dir = "linux-x86_64"
        elif machine in ("aarch64", "arm64"):
            platform_dir = "linux-aarch64"
        else:
            raise RuntimeError(f"Unsupported Linux architecture: {machine}")
    elif system == "darwin":
        if machine in ("arm64", "aarch64"):
            platform_dir = "darwin-arm64"
        elif machine in ("x86_64", "amd64"):
            platform_dir = "darwin-x86_64"
        else:
            raise RuntimeError(f"Unsupported macOS architecture: {machine}")
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")
    
    bin_package = files("dwf_sim.bin") / platform_dir
    ngsngs_ref = bin_package / "ngsngs"
    return Path(str(ngsngs_ref))
