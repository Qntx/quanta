from importlib.util import find_spec
import os
import subprocess
import sys
import ensurepip
from typing import Dict, Optional, Tuple
from art import tprint
from loguru import logger


def print_banner():
    """Print stylized Quanta banner using ASCII art.

    Uses the art library's tprint function with the alpha font to create
    an ASCII art banner displaying "Quanta".
    """
    tprint("Quanta", font="alpha")


def check_and_install_package(
    package_name: str, package_url: Optional[str] = None
) -> Tuple[bool, str]:
    """Check if a Python package is installed and install if needed.

    Args:
        package_name (str): Name of the package to check/install
        package_url (Optional[str], optional): URL or path to the package to install.
            If empty, install from PyPI. Defaults to None.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if installation successful, False otherwise
            - str: Status message describing the result
    """
    if not package_name:
        return False, "Package name cannot be empty"

    # Check if package is already installed
    if find_spec(package_name) is not None:
        return True, f"{package_name} package is already installed"

    logger.warning(f"{package_name} package is not installed, attempting to install...")

    try:
        # Ensure pip is available and up to date
        ensurepip.bootstrap(upgrade=True)

        # Determine install source
        install_target = package_url if package_url is not None else package_name
        source = "from " + (package_url if package_url is not None else "PyPI")

        # Install package using pip
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", install_target],
            stderr=subprocess.PIPE,
        )

        # Verify installation was successful
        if find_spec(package_name) is not None:
            return True, f"Successfully installed {package_name} package {source}"
        else:
            return False, f"Package installation completed but {package_name} not found"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to install {package_name} package {source}: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error installing {package_name}: {str(e)}"


def check_env_vars() -> Tuple[bool, Dict[str, str], str]:
    """
    Check required environment variables.
    Returns:
        Tuple containing:
        - Boolean indicating if all required vars are present
        - Dict of environment variables
        - Success/error message
    """
    env_vars: Dict[str, str] = {}
    required_vars = ["HTTP_PROXY", "WS_PROXY", "API_KEY", "SECRET", "PASSWORD"]

    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            return (
                False,
                env_vars,
                f"Missing required environment variables: {var}",
            )
        env_vars[var] = value

    return True, env_vars, "All required environment variables are present"
