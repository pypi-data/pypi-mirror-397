import logging
import time
import webbrowser

from fastapi import FastAPI
from rich.console import Console

from autreach.cli.server.health import wait_for_server
from autreach.cli.server.port import resolve_port
from autreach.cli.server.uvicorn_server import UvicornServer

console = Console()


def run_studio_server(app: FastAPI, host: str, port: int):
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("autreach").setLevel(logging.WARNING)

    port = resolve_port(host, port)
    url = f"http://{host}:{port}"

    server = UvicornServer(app, host, port)
    server.start()

    console.print("[bold blue]🚀 Starting Autreach Studio...[/bold blue]")

    with console.status("[bold yellow]Waiting for server to start...", spinner="dots"):
        ready = wait_for_server(url)

    if not ready:
        console.print(
            "[bold red]✗ Server failed to start within timeout period[/bold red]"
        )
        server.stop()
        return

    console.print("[bold green]✓ Server is ready![/bold green]")
    console.print(f"[cyan]Opening browser at {url}[/cyan]")
    webbrowser.open(url)
    console.print("\n[bold]Server is running. Press [red]Ctrl+C[/red] to stop.[/bold]")

    try:
        while server.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down server...[/bold yellow]")
        server.stop()
        console.print("[bold green]✓ Server stopped[/bold green]")
