import importlib.resources as pkg_resources
from pathlib import Path

from fastapi.responses import FileResponse, HTMLResponse


def get_static_dir() -> Path | None:
    try:
        # Inline import since this wouldn't work in local development
        import autreach.ui

        ui_path = Path(autreach.ui.__file__).parent
        if ui_path.exists() and ui_path.is_dir() and (ui_path / "index.html").exists():
            return ui_path
    except (ModuleNotFoundError, AttributeError):
        pass

    try:
        ui_files = pkg_resources.files("autreach.ui")
        ui_path = Path(str(ui_files))
        if ui_path.exists() and ui_path.is_dir() and (ui_path / "index.html").exists():
            return ui_path
    except (ModuleNotFoundError, TypeError, AttributeError):
        pass

    # For local development
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent.parent.parent
    static_dir = project_root / "studio-ui" / "dist"
    if static_dir.exists() and static_dir.is_dir():
        return static_dir

    return None


def serve_index_html(static_dir: Path | None) -> FileResponse | HTMLResponse:
    if static_dir and (static_dir / "index.html").exists():
        return FileResponse(str(static_dir / "index.html"))
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Autreach Studio - Build Required</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 3rem;
                    border-radius: 1rem;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 600px;
                }
                h1 {
                    color: #333;
                    margin: 0 0 1rem 0;
                    font-size: 2rem;
                }
                p {
                    color: #666;
                    font-size: 1.1rem;
                    margin: 1rem 0;
                }
                code {
                    background: #f4f4f4;
                    padding: 0.2rem 0.5rem;
                    border-radius: 0.25rem;
                    font-family: 'Courier New', monospace;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Build Required</h1>
                <p>The React app has not been built yet.</p>
                <p>Please run <code>cd studio-ui && pnpm build</code> to build the app.</p>
            </div>
        </body>
        </html>
        """,
        status_code=200,
    )
