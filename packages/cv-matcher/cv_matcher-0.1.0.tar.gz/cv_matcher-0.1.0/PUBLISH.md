# Publishing to PyPI

This guide explains how to publish the cv-matcher package to PyPI Test and production PyPI.

## Prerequisites

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

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml` and increment the version:
```toml
version = "0.3.0"  # Increment this
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/cv_matcher-0.3.0-py3-none-any.whl`
- `dist/cv_matcher-0.3.0.tar.gz`

### 3. Test Locally (Optional)

```bash
# Install in a new environment
uv venv test-env
source test-env/bin/activate
uv pip install dist/cv_matcher-0.3.0-py3-none-any.whl

# Test it
python -c "from cv_matcher import CVMatcher; print('✓ Import successful!')"
```

### 4. Upload to Test PyPI

```bash
# Upload using your Test PyPI token
twine upload --repository testpypi dist/*

# Or with explicit credentials
twine upload --repository-url https://test.pypi.org/legacy/ dist/* \
  --username __token__ \
  --password <your-testpypi-token>
```

### 5. Test Installation from Test PyPI

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

### 6. Upload to Production PyPI

Once testing is successful:

```bash
# Upload to production PyPI
twine upload dist/*

# Or with explicit credentials
twine upload dist/* \
  --username __token__ \
  --password <your-pypi-token>
```

### 7. Verify Installation

```bash
# Install from production PyPI
pip install cv-matcher

# Verify
python -c "from cv_matcher import CVMatcher; print('✓ Production install successful!')"
```

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

## Environment Variables

You can also use environment variables for credentials:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-token>
twine upload dist/*
```

## Checklist Before Publishing

- [ ] All tests pass
- [ ] README is up to date
- [ ] CHANGELOG is updated
- [ ] Version number incremented in `pyproject.toml`
- [ ] Git tag created: `git tag v0.3.0 && git push origin v0.3.0`
- [ ] Clean build directory
- [ ] Built package successfully
- [ ] Tested on Test PyPI
- [ ] Ready for production

## Troubleshooting

**Error: File already exists**
- You cannot overwrite existing versions on PyPI
- Increment the version number and rebuild

**Error: Invalid credentials**
- Ensure you're using API tokens, not passwords
- Username should be `__token__`
- Check token has correct permissions

**Missing dependencies on Test PyPI**
- Some dependencies might not exist on Test PyPI
- Use `--extra-index-url https://pypi.org/simple/` when installing

## Automated Publishing with GitHub Actions

See `.github/workflows/publish.yml` for automated publishing on git tag push.

```bash
# Create and push a tag to trigger automated publish
git tag v0.3.0
git push origin v0.3.0
```
