import typer
import sys
import ccxt.pro as ccxt
import asyncio
import os
from loguru import logger
from dotenv import load_dotenv
from typing import List
from pathlib import Path
from copier import run_copy

from qnta.utils import check_and_install_quantum, print_banner
from quantum.broker.broker_manager import BrokerManager

app = typer.Typer()

# Load .env from current working directory
load_dotenv(dotenv_path=Path(os.getcwd()) / ".env")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.command()
def init(
    template: str = "gh:Qntx/quanta-template",
    path: str = ".",
    project_name: str = typer.Option(..., prompt=True, help="Name of the project"),
    module_name: str = typer.Option(..., prompt=True, help="Name of the module"),
):
    """
    Initialize the package by installing required dependencies and setting up project from template.

    Args:
        template: Git repository template to use (default: gh:Qntx/quanta-template)
        path: Target directory path for project initialization (default: current directory)
        project_name: Name of the project (will be prompted if not provided)
        module_name: Name of the module (will be prompted if not provided)
    """
    success, message = check_and_install_quantum()
    if not success:
        logger.error(message)
        raise typer.Exit(1)
    logger.success(message)

    try:
        logger.info("Initializing project from template...")
        run_copy(
            src_path=template,
            dst_path=path,
            data={"project_name": project_name, "module_name": module_name},
            defaults=True,
            unsafe=True,
        )
        logger.success("Successfully initialized project from template!")
    except Exception as e:
        logger.error(f"Failed to initialize project from template: {str(e)}")
        raise typer.Exit(1)


@app.command()
def run():
    """
    Run the quantum program.
    """
    success, message = check_and_install_quantum()
    if not success:
        logger.warning(message)
        raise typer.Exit(1)

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
    Monitor exchange account data and execution status via command line interface.

    This command connects to the specified exchange and provides real-time monitoring of:
    - Account balances and positions
    - Open orders and execution status
    - Market data for specified trading symbols
    - Trading activities and performance metrics

    Args:
        broker: Broker name in format 'provider:exchange' (e.g. 'ccxt:bitget')
        symbols: List of trading symbols to monitor
        mode: Trading mode ('paper' for simulation or 'live' for real trading)
        type: Market type ('swap' for perpetual futures, 'spot' for spot trading, etc)
    """
    success, message = check_and_install_quantum()
    if not success:
        logger.warning(message)
        raise typer.Exit(1)

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
    app()
