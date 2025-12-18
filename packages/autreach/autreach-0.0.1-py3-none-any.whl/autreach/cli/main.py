import typer

from autreach.api.main import app as fastapi_app
from autreach.cli.server import run_studio_server

cli = typer.Typer(
    name="autreach",
    help="Autreach CLI - Outreach automation toolkit",
    no_args_is_help=True,
)


@cli.command()
def studio(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the server on"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
):
    run_studio_server(fastapi_app, host, port)


def main():
    cli()


if __name__ == "__main__":
    main()
