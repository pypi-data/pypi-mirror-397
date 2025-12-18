# PyPI Publishing Configuration Guide

This guide explains how to configure credentials for publishing the `autreach` package to PyPI and TestPyPI.

## Trusted Publishing with OpenID Connect (OIDC) - Recommended

Trusted Publishing is the recommended method as it doesn't require storing API tokens as secrets. GitHub Actions authenticates directly with PyPI using OpenID Connect.

### Setting Up Trusted Publishing on PyPI

1. **Log in to PyPI:**

   - Go to [pypi.org](https://pypi.org) and log in to your account
   - If you don't have an account, create one at [pypi.org/account/register/](https://pypi.org/account/register/)

2. **Create a New Project (if not already created):**

   - Go to [pypi.org/manage/projects/](https://pypi.org/manage/projects/)
   - Click "Add new project"
   - Enter the project name: `autreach`
   - Click "Create"

3. **Configure Trusted Publishing:**
   - Navigate to your project's management page: [pypi.org/manage/project/autreach/](https://pypi.org/manage/project/autreach/)
   - Go to the "Publishing" section
   - Click "Add a new publisher"
   - Select "GitHub Actions" as the publisher type
   - Fill in the required details:
     - **Owner:** Your GitHub username or organization name
     - **Repository:** `autreach` (or your repository name)
     - **Workflow filename:** `publish.yml`
     - **Environment name (optional):** `pypi`
   - Click "Add" to create the trusted publisher

### Setting Up Trusted Publishing on TestPyPI

1. **Log in to TestPyPI:**

   - Go to [test.pypi.org](https://test.pypi.org) and log in
   - If you don't have an account, create one at [test.pypi.org/account/register/](https://test.pypi.org/account/register/)

2. **Create a New Project:**

   - Go to [test.pypi.org/manage/projects/](https://test.pypi.org/manage/projects/)
   - Click "Add new project"
   - Enter the project name: `autreach`
   - Click "Create"

3. **Configure Trusted Publishing:**
   - Navigate to your project's management page
   - Go to the "Publishing" section
   - Click "Add a new publisher"
   - Select "GitHub Actions"
   - Fill in the same details as for PyPI:
     - **Owner:** Your GitHub username or organization name
     - **Repository:** `autreach`
     - **Workflow filename:** `publish.yml`
     - **Environment name (optional):** `testpypi`
   - Click "Add"

### Configuring GitHub Environments (Optional but Recommended)

For better security and control, you can create GitHub Environments:

1. **In your GitHub repository:**
   - Go to Settings → Environments
   - Click "New environment"
   - Create an environment named `pypi`
   - Create another environment named `testpypi`
   - These environments will be referenced in the workflow file

The workflow file (`.github/workflows/publish.yml`) is already configured to use these environments.

## Alternative: Using API Tokens

If you prefer to use API tokens instead of trusted publishing:

### Generating API Tokens on PyPI

1. **Log in to PyPI** and go to [pypi.org/manage/account/](https://pypi.org/manage/account/)
2. **Navigate to API tokens:**
   - Scroll to the "API tokens" section
   - Click "Add API token"
3. **Configure the token:**
   - Provide a name (e.g., "GitHub Actions - autreach")
   - Set the scope to "Entire account" or limit to the `autreach` project
   - Click "Add token"
4. **Copy the token:**
   - The token will be shown only once (format: `pypi-...`)
   - Copy it immediately

### Generating API Tokens on TestPyPI

1. **Log in to TestPyPI** and go to [test.pypi.org/manage/account/](https://test.pypi.org/manage/account/)
2. Follow the same steps as above to generate a token

### Storing Tokens in GitHub Secrets

1. **In your GitHub repository:**

   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Create secrets:
     - Name: `PYPI_API_TOKEN`, Value: your PyPI API token
     - Name: `TEST_PYPI_API_TOKEN`, Value: your TestPyPI API token

2. **Update the workflow file:**

   - Modify `.github/workflows/publish.yml` to use the tokens instead of trusted publishing
   - Replace the `pypa/gh-action-pypi-publish` steps with:

     ```yaml
     - name: Publish to PyPI
       env:
         TWINE_USERNAME: __token__
         TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
       run: |
         uv pip install twine
         twine upload dist/*
     ```

## Release Process

### Automatic Release via Git Tags

The workflow automatically triggers when you push a git tag:

- **Pre-releases** (tags containing `-`, e.g., `v0.1.0-alpha`, `v0.1.0-beta`):
  - Published to TestPyPI only
- **Releases** (tags without `-`, e.g., `v0.1.0`, `v0.2.0`):
  - Published to PyPI

**To create a release:**

```bash
# Create and push a release tag
git tag v0.1.0
git push origin v0.1.0

# Or create a pre-release tag
git tag v0.1.0-alpha
git push origin v0.1.0-alpha
```

### Manual Release via Workflow Dispatch

You can also trigger a release manually:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Publish to PyPI" workflow
3. Click "Run workflow"
4. Enter the version tag (e.g., `v0.1.0`)
5. Click "Run workflow"

Note: Manual dispatch still requires a valid git tag to be present in the repository.

## Verifying the Release

After publishing:

1. **Check PyPI:**

   - Visit [pypi.org/project/autreach/](https://pypi.org/project/autreach/)
   - Verify the new version appears

2. **Check TestPyPI:**

   - Visit [test.pypi.org/project/autreach/](https://test.pypi.org/project/autreach/)
   - Verify pre-release versions appear

3. **Test Installation:**

   ```bash
   # Test from PyPI
   pip install autreach

   # Test from TestPyPI (use PyPI as primary, TestPyPI as fallback for autreach only)
   pip install --index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/ autreach
   ```

## Troubleshooting

### Build Fails with "pnpm: command not found"

- Ensure the workflow includes the pnpm setup step (already included in the workflow)

### Publishing Fails with Authentication Error

- Verify trusted publishing is configured correctly on PyPI/TestPyPI
- Check that the GitHub repository name, owner, and workflow filename match exactly
- For API tokens, verify the secrets are set correctly in GitHub

### UI Assets Not Included in Package

- Ensure the build hook (`hatch_build.py`) runs successfully
- Check that `src/autreach/ui/` directory exists after the build
- Verify `pyproject.toml` includes the `ui/` directory in the package

### Installation from TestPyPI Fails with Dependency Errors

TestPyPI may contain broken or incomplete versions of dependencies (like `fastapi`). To ensure all dependencies come from PyPI while installing `autreach` from TestPyPI, use a two-step installation:

**Step 1:** Install `autreach` without dependencies from TestPyPI:

```bash
pip install --no-deps --index-url https://test.pypi.org/simple/ autreach
```

**Step 2:** Install all dependencies from PyPI:

```bash
pip install "colorama>=0.4.6" "fastapi[standard]>=0.115.12" "pydantic-settings>=2.9.1" "selenium>=4.32.0" "sqlmodel>=0.0.14" "typer>=0.9.0" "uvicorn>=0.27.0"
```

**Alternative (if the above doesn't work):** You can also try installing with PyPI as primary and TestPyPI as extra index, but pip may still prefer broken packages from TestPyPI:

```bash
pip install --index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/ autreach
```

If this still fails, use the two-step method above.

## Additional Resources

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [TestPyPI Documentation](https://test.pypi.org/help/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
