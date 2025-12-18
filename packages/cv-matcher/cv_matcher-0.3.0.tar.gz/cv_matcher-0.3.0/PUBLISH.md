# Publishing to PyPI and Docker Hub

This guide explains how to publish the cv-matcher package to PyPI and Docker Hub.

## Prerequisites

### For PyPI:
1. **Create accounts:**
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

2. **Generate API tokens:**
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - Production PyPI: https://pypi.org/manage/account/token/

3. **Install build tools:**
   ```bash
   uv pip install build twine
   ```

### For Docker Hub:
1. **Create account:**
   - Docker Hub: https://hub.docker.com/signup

2. **Generate access token:**
   - Go to Account Settings > Security
   - Click "New Access Token"
   - Give it a description (e.g., "GitHub Actions")
   - Save the token

## GitHub Actions Automated Publishing

### Setup GitHub Secrets

Go to your repository Settings > Secrets and variables > Actions, and add:

**PyPI Secrets:**
- `PYPI_TOKEN`: Your PyPI API token
- `TEST_PYPI_TOKEN`: Your Test PyPI API token

**Docker Hub Secrets:**
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token (not your password!)

### Publishing Process

1. **Update Version**
   ```bash
   # Edit pyproject.toml and increment version
   version = "0.3.0"
   ```

2. **Commit and Push**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.3.0"
   git push
   ```

3. **Create Git Tag**
   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```

4. **Create GitHub Release**
   - Go to repository > Releases > Create a new release
   - Choose the tag (v0.3.0)
   - Add release title and notes
   - Click "Publish release"

5. **Automated Publishing**
   
   GitHub Actions will automatically:
   - ✅ Build Python package
   - ✅ Publish to Test PyPI
   - ✅ Publish to PyPI
   - ✅ Build Docker image (multi-platform: amd64, arm64)
   - ✅ Push to Docker Hub with version tag and 'latest'
   - ✅ Update Docker Hub repository description

   Monitor at: `https://github.com/YOUR_USERNAME/cv-matcher/actions`

## Manual Publishing (if needed)

### PyPI Publishing

### 1. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/cv_matcher-0.3.0-py3-none-any.whl`
- `dist/cv_matcher-0.3.0.tar.gz`

### 2. Test Locally (Optional)

```bash
# Install in a new environment
uv venv test-env
source test-env/bin/activate
uv pip install dist/cv_matcher-0.3.0-py3-none-any.whl

# Test it
python -c "from cv_matcher import CVMatcher; print('✓ Import successful!')"
```

### 3. Upload to Test PyPI

```bash
# Upload using your Test PyPI token
twine upload --repository testpypi dist/*

# Or with explicit credentials
twine upload --repository-url https://test.pypi.org/legacy/ dist/* \
  --username __token__ \
  --password <your-testpypi-token>
```

### 4. Test Installation from Test PyPI

```bash
# Create new environment
uv venv test-install
source test-install/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  cv-matcher

# Test it
python -c "from cv_matcher import CVMatcher; print('✓ Installation successful!')"
```

Note: `--extra-index-url` is needed because Test PyPI may not have all dependencies.

### 5. Upload to Production PyPI

Once testing is successful:

```bash
# Upload to production PyPI
twine upload dist/*

# Or with explicit credentials
twine upload dist/* \
  --username __token__ \
  --password <your-pypi-token>
```

### 6. Verify Installation

```bash
# Install from production PyPI
pip install cv-matcher

# Verify
python -c "from cv_matcher import CVMatcher; print('✓ Production install successful!')"
```

### Docker Publishing

### 1. Build Docker Image

```bash
# Build for current platform
docker build -t YOUR_USERNAME/cv-matcher:0.3.0 .
docker tag YOUR_USERNAME/cv-matcher:0.3.0 YOUR_USERNAME/cv-matcher:latest
```

### 2. Test Locally

```bash
# Run the container
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key YOUR_USERNAME/cv-matcher:0.3.0

# Open http://localhost:7860 in browser to test
```

### 3. Push to Docker Hub

```bash
# Log in to Docker Hub
docker login

# Push images
docker push YOUR_USERNAME/cv-matcher:0.3.0
docker push YOUR_USERNAME/cv-matcher:latest
```

### 4. Multi-Platform Build (Optional)

For both amd64 and arm64 support:

```bash
# Create buildx builder (one-time setup)
docker buildx create --use

# Build and push for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t YOUR_USERNAME/cv-matcher:0.3.0 \
  -t YOUR_USERNAME/cv-matcher:latest \
  --push .
```

## Using Published Docker Image

Users can pull and run your image:

```bash
# Pull latest version
docker pull YOUR_USERNAME/cv-matcher:latest

# Run with OpenAI
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key YOUR_USERNAME/cv-matcher:latest

# Run with local models
docker run -p 7860:7860 -e USE_LOCAL_MODEL=true YOUR_USERNAME/cv-matcher:latest

# Or specific version
docker pull YOUR_USERNAME/cv-matcher:0.3.0
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key YOUR_USERNAME/cv-matcher:0.3.0
```

## Verification

### Verify PyPI Package:
```bash
pip install cv-matcher
python -c "from cv_matcher import CVMatcher; print('Works!')"
```

### Verify Docker Image:
```bash
docker pull YOUR_USERNAME/cv-matcher:latest
docker images | grep cv-matcher
```

Visit Docker Hub: `https://hub.docker.com/r/YOUR_USERNAME/cv-matcher`


## Using uv for Publishing

If you prefer using `uv`:

```bash
# Build
uv build

# Publish to Test PyPI
uv publish --repository testpypi

# Publish to Production PyPI
uv publish
```

## Troubleshooting

### PyPI Issues:
- **File already exists**: Cannot overwrite versions, increment version number
- **Invalid credentials**: Use API tokens with `__token__` as username
- **Missing dependencies on Test PyPI**: Use `--extra-index-url https://pypi.org/simple/`

### Docker Issues:
- **Authentication failed**: Run `docker login` and verify credentials
- **Name invalid**: Docker Hub username must be lowercase  
- **Push timeout**: Check internet connection or retry
- **Platform mismatch**: Use buildx for multi-platform builds

### GitHub Actions:
- Check Actions tab for detailed logs
- Verify all secrets are set correctly (PYPI_TOKEN, DOCKER_USERNAME, DOCKER_PASSWORD)
- Ensure tag format is `v0.3.0` (with 'v' prefix)
- Make sure workflows have necessary permissions

## Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md with release notes
- [ ] Run tests locally: `uv run pytest`
- [ ] Run linting: `black . && ruff check .`
- [ ] Commit and push all changes
- [ ] Create and push git tag: `git tag v0.3.0 && git push origin v0.3.0`
- [ ] Create GitHub release with notes
- [ ] Monitor GitHub Actions workflows (PyPI + Docker)
- [ ] Verify PyPI package: `pip install cv-matcher`
- [ ] Verify Docker Hub image: `docker pull YOUR_USERNAME/cv-matcher:latest`
- [ ] Test both installations work correctly
- [ ] Update documentation if needed

