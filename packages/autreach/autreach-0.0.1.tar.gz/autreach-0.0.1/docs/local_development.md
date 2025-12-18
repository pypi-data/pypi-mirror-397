# Local Development

Run the following commands in the root of the project.

```bash
uv sync
source .venv/bin/activate
```

Running the API:

```bash
uv run python3 src/autreach/api/main.py
```

Running the CLI:

```bash
uv run python3 src/autreach/cli/main.py
```

```bash
uv pip install -e .
uv pip uninstall autreach




cd studio-ui && pnpm dev

. Build the Frontend
cd studio-ui
pnpm install --frozen-lockfile
pnpm build
cd studio-uipnpm install --frozen-lockfilepnpm build 2. Build the Python Package
The hatch_build.py hook will automatically:
Run pnpm build in studio-ui/
Copy the built frontend to src/autreach/ui/

# Install build dependencies

uv pip install build hatchling

# Build the package (creates dist/ with .whl and .tar.gz)

uv build

# Install build dependenciesuv pip install build hatchling# Build the package (creates dist/ with .whl and .tar.gz)uv build

3. Publish to PyPI
   For TestPyPI (pre-release versions with - in tag like v0.1.0-beta):
   uv pip install twine
   twine upload --repository testpypi dist/_
   uv pip install twinetwine upload --repository testpypi dist/_
   For Production PyPI:
   uv pip install twine
   twine upload dist/_
   uv pip install twinetwine upload dist/_
   You'll need to configure your PyPI credentials either via:
   ~/.pypirc file
   Environment variables: TWINE_USERNAME and TWINE_PASSWORD (or TWINE_API_TOKEN)
   Using API Token (Recommended)

# For PyPI

twine upload -u **token** -p <your-pypi-api-token> dist/\*

# For TestPyPI

twine upload --repository testpypi -u **token** -p <your-testpypi-api-token> dist/\*

# For PyPItwine upload -u **token** -p <your-pypi-api-token> dist/_# For TestPyPItwine upload --repository testpypi -u **token** -p <your-testpypi-api-token> dist/_

Quick One-Liner
cd studio-ui && pnpm install && cd .. && uv build && twine upload dist/_
cd studio-ui && pnpm install && cd .. && uv build && twine upload dist/_
```

rm -rf dist/ build/ \*.egg-info src/autreach/ui/ studio-ui/dist/

find . -type d -name **pycache** -exec rm -rf {} +
