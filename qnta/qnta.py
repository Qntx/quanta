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

from qnta.utils.util import check_env_vars

app = typer.Typer(help="Qnta CLI - A powerful tool for quantum trading")

# Load .env from current working directory
load_dotenv(dotenv_path=Path(os.getcwd()) / ".env")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.command()
def init(
    template: str = typer.Option(
        "gh:Qntx/quanta-template",
        "--template",
        "-t",
        help="Git repository template to use for project initialization",
    ),
    path: str = typer.Option(
        ".", "--path", "-p", help="Target directory path for project initialization"
    ),
    project_name: str = typer.Option(
        ...,
        prompt=True,
        help="Name of the project - Used for package naming and documentation",
    ),
    module_name: str = typer.Option(
        ...,
        prompt=True,
        help="Name of the module - Used for importing and internal references",
    ),
):
    """
    Initialize a new quantum trading project with required dependencies and template structure.

    This command will:
    1. Check and install quantum dependencies
    2. Create project structure from template
    3. Set up configuration files
    4. Initialize git repository if needed
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
def check():
    """
    Verify quantum environment configuration and dependencies.

    Checks:
    - Python environment and version
    - Required packages installation
    - System dependencies
    - Configuration files
    """
    # Check and install quantum
    success, message = check_and_install_quantum()
    if not success:
        logger.error(message)
        raise typer.Exit(1)
    logger.success(message)

    # Check required environment variables
    env_success, _, error_msg = check_env_vars()
    if not env_success:
        logger.error(error_msg)
        logger.info("Please add the missing variables to your .env file")
        raise typer.Exit(1)
    logger.success("Quantum environment configuration is correct!")


@app.command()
def run():
    """
    Execute the quantum trading program.

    This command:
    1. Verifies environment setup
    2. Loads trading configurations
    3. Initializes trading engine
    4. Starts trading operations
    """
    success, message = check_and_install_quantum()
    if not success:
        logger.warning(message)
        raise typer.Exit(1)

    print_banner()
    logger.info("Starting quantum program...")


@app.command()
def monitor(
    broker: str = typer.Option(
        "ccxt:bitget",
        "--broker",
        "-b",
        help="Broker identifier in format 'provider:exchange' (e.g. 'ccxt:bitget')",
    ),
    symbols: List[str] = typer.Option(
        ["SBTC/SUSDT:SUSDT"],
        "--symbols",
        "-s",
        help="Trading symbols to monitor (e.g. 'BTC/USDT')",
    ),
    mode: str = typer.Option(
        "paper",
        "--mode",
        "-m",
        help="Trading mode: 'paper' for simulation, 'live' for real trading",
    ),
    type: str = typer.Option(
        "swap",
        "--type",
        "-t",
        help="Market type: 'swap' for perpetual futures, 'spot' for spot trading",
    ),
):
    """
    Monitor exchange account data and execution status via command line interface.

    This command provides real-time monitoring of:
    - Account balances and positions
    - Open orders and execution status
    - Market data for specified trading symbols
    - Trading activities and performance metrics
    - Risk management indicators
    - P&L tracking
    """
    # Check and install quantum
    success, message = check_and_install_quantum()
    if not success:
        logger.warning(message)
        raise typer.Exit(1)

    logger.info(
        f"Starting trading bot with broker: {broker}, symbols: {symbols}, mode: {mode}"
    )

    # Check required environment variables
    env_success, env_vars, error_msg = check_env_vars()
    if not env_success:
        logger.error(error_msg)
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
                "httpsProxy": env_vars["HTTP_PROXY"],
                "wsProxy": env_vars["WS_PROXY"],
                "apiKey": env_vars["API_KEY"],
                "secret": env_vars["SECRET"],
                "password": env_vars["PASSWORD"],
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
