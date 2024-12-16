from importlib.util import find_spec
import os
import subprocess
import sys
import ensurepip
from typing import Dict, Tuple
from art import tprint
from loguru import logger


def print_banner():
    """Print stylized Quanta banner using ASCII art.

    Uses the art library's tprint function with the alpha font to create
    an ASCII art banner displaying "Quanta".
    """
    tprint("Quanta", font="alpha")


def check_and_install_quantum() -> Tuple[bool, str]:
    """
    Check if quantum package is installed and install if needed.
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if find_spec("quantum") is None:
        logger.warning("Quantum package is not installed, attempting to install...")
        try:
            # Ensure pip is available
            ensurepip.bootstrap(upgrade=True)

            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-U",
                    "git+https://github.com/qntx/Quantum.git",
                ]
            )
            return True, "Successfully installed quantum package!"
        except subprocess.CalledProcessError:
            return (
                False,
                "Failed to install quantum package. Please try running with administrator privileges.",
            )
    return True, "Quantum package is already installed"


def check_env_vars() -> Tuple[bool, Dict[str, str], str]:
    """
    Check required environment variables.
    Returns:
        Tuple containing:
        - Boolean indicating if all required vars are present
        - Dict of environment variables
        - Error message if any vars are missing
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

    return True, env_vars, ""
