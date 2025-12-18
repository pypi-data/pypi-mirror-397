import asyncio
import threading

import uvicorn
from fastapi import FastAPI


class UvicornServer:
    def __init__(self, app: FastAPI, host: str, port: int):
        config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        asyncio.run(self.server.serve())

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.should_exit = True
        self.thread.join(timeout=5)

    def is_alive(self) -> bool:
        return self.thread.is_alive()
