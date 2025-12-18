import socket

from rich.console import Console

console = Console()


def is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(host: str, start_port: int, max_attempts: int = 100) -> int:
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(host, port):
            return port
    raise RuntimeError(
        f"No available port found in range {start_port}-{start_port + max_attempts - 1}"
    )


def resolve_port(host: str, port: int) -> int:
    if is_port_available(host, port):
        return port
    new_port = find_available_port(host, port + 1)
    console.print(
        f"[yellow]Port {port} is in use, using port {new_port} instead[/yellow]"
    )
    return new_port
