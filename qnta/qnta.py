import typer
import subprocess
import sys
from importlib.util import find_spec
from loguru import logger

from qnta.utils.util import print_banner

app = typer.Typer()


@app.command()
def init():
    """
    Initialize the package by installing required dependencies.
    """
    if find_spec("quantum") is None:
        logger.info("Installing quantum package...")
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "git+https://github.com/qntx/Quantum.git",
                ]
            )
            logger.success("Successfully installed quantum package!")
        except subprocess.CalledProcessError:
            logger.error("Failed to install quantum package")
            raise typer.Exit(1)
    else:
        logger.info("Quantum package is already installed")


@app.command()
def run():
    """
    Run the quantum program.
    """
    print_banner()
    logger.info("Starting quantum program...")


if __name__ == "__main__":
    # Configure logger
    logger.add("qnta.log", rotation="500 MB")
    app()
