import typer

from qnta.utils.util import print_banner

app = typer.Typer()


@app.command()
def hello(name: str):
    """
    Greet a user by their name.
    """
    typer.echo(f"Hello {name}!")


@app.command()
def add(a: int, b: int):
    """
    Add two numbers.
    """
    typer.echo(f"The result is {a + b}")


@app.command()
def run():
    """
    Run the quantum program.
    """
    print_banner()
    typer.echo("Running the quantum program...")


if __name__ == "__main__":
    app()
