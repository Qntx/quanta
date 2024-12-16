import typer
import subprocess
import sys
import ccxt.pro as ccxt
import asyncio
import os
from importlib.util import find_spec
from loguru import logger
from dotenv import load_dotenv
from typing import List

from qnta.utils.util import print_banner
from quantum.broker.broker_manager import BrokerManager

app = typer.Typer()

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


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
                    "-U",
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


@app.command()
def monitor(
    broker: str = "ccxt:bitget",
    symbols: List[str] = ["SBTC/SUSDT:SUSDT"],
    mode: str = "paper",
    type: str = "swap",
):
    """
    Run the trading bot with specified symbols and mode.

    Args:
        broker: Broker name in format 'provider:exchange' (e.g. 'ccxt:bitget')
        symbols: List of trading symbols
        mode: Trading mode ('paper' or 'live')
        type: Market type ('swap', 'spot', etc)
    """
    logger.info(
        f"Starting trading bot with broker: {broker}, symbols: {symbols}, mode: {mode}"
    )

    # Check required environment variables
    required_env_vars = {
        "HTTP_PROXY": os.getenv("HTTP_PROXY"),
        "WS_PROXY": os.getenv("WS_PROXY"),
        "API_KEY": os.getenv("API_KEY"),
        "SECRET": os.getenv("SECRET"),
        "PASSWORD": os.getenv("PASSWORD"),
    }

    missing_vars = [var for var, value in required_env_vars.items() if value is None]
    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.info("Please add the missing variables to your .env file")
        raise typer.Exit(1)

    # Parse broker name
    provider, exchange_name = broker.split(":")
    if provider != "ccxt":
        logger.error(f"Unsupported broker provider: {provider}")
        raise typer.Exit(1)

    # Create exchange instance
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class(
            {
                "httpsProxy": required_env_vars["HTTP_PROXY"],
                "wsProxy": required_env_vars["WS_PROXY"],
                "apiKey": required_env_vars["API_KEY"],
                "secret": required_env_vars["SECRET"],
                "password": required_env_vars["PASSWORD"],
                "options": {"defaultType": type},
            }
        )
    except (AttributeError, ValueError) as e:
        logger.error(f"Failed to create exchange instance: {e}")
        raise typer.Exit(1)

    # Initialize broker manager
    broker_manager = BrokerManager()

    # Get broker instance
    broker_instance = broker_manager.B(
        broker_id=broker,
        exchange=exchange,
        symbols=symbols,
        mode=mode,
        market_type=type,
        debug=True,
    )

    if broker_instance is None:
        logger.error("Failed to create broker instance")
        raise typer.Exit(1)

    asyncio.run(broker_instance.run())


if __name__ == "__main__":
    # Configure logger
    logger.add("qnta.log", rotation="500 MB")
    app()
