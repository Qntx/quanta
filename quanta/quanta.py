import typer

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


if __name__ == "__main__":
    app()
