# Publishing Guide

This guide covers how to publish the Quantum Simulator package to PyPI and deploy the documentation to GitHub Pages.

## Publishing to PyPI

### Prerequisites

1. **Create PyPI Account**: Sign up at [pypi.org](https://pypi.org/account/register/)
2. **Install Build Tools**: 
   ```bash
   pip install build twine
   ```
3. **API Token**: Create an API token at [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

### Step-by-Step Publishing

#### 1. Prepare the Release

Update the version in `src/quantum_simulator/__init__.py`:
```python
__version__ = "0.2.0"  # Increment version number
```

Update `CHANGELOG.md` with release notes.

#### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build
```

This creates:
- `dist/quantum_simulator-0.2.0.tar.gz` (source distribution)
- `dist/quantum_simulator-0.2.0-py3-none-any.whl` (wheel)

#### 3. Test the Build

Test your package locally:
```bash
pip install dist/quantum_simulator-0.2.0-py3-none-any.whl
```

#### 4. Upload to TestPyPI (Optional)

Test on TestPyPI first:
```bash
twine upload --repository testpypi dist/*
```

#### 5. Upload to PyPI

```bash
twine upload dist/*
```

Enter your username and API token when prompted.

### Automated Publishing with GitHub Actions

The repository includes automated publishing via GitHub Actions. To enable:

1. **Add PyPI Token to GitHub Secrets**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` with your PyPI API token

2. **Create a Release**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

3. **GitHub Actions** will automatically:
   - Run tests
   - Build the package
   - Publish to PyPI

## Deploying Documentation

### Manual Deployment

Build and deploy documentation:
```bash
# Install documentation dependencies
pip install -e .[docs]

# Build the documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Automated Deployment with GitHub Actions

Documentation is automatically deployed on push to `main` branch.

The workflow:
1. **Builds** the documentation using MkDocs
2. **Deploys** to GitHub Pages
3. **Available** at: `https://beefy.github.io/quantum-simulator/`

### Custom Domain (Optional)

To use a custom domain:

1. **Add CNAME file** to `docs/`:
   ```
   docs.quantum-simulator.com
   ```

2. **Configure DNS** to point to `beefy.github.io`

3. **Enable HTTPS** in repository settings

## Version Management

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)  
- **PATCH**: Bug fixes (backward compatible)

### Pre-release Versions

For development versions:
- `1.0.0a1` (alpha)
- `1.0.0b1` (beta) 
- `1.0.0rc1` (release candidate)

### Version Bumping

1. **Update** `src/quantum_simulator/__init__.py`
2. **Update** `CHANGELOG.md` 
3. **Commit** changes
4. **Tag** the release:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Release Checklist

Before each release:

- [ ] Update version number
- [ ] Update CHANGELOG.md
- [ ] Run tests: `pytest`
- [ ] Build documentation: `mkdocs build`
- [ ] Test package build: `python -m build`
- [ ] Test installation: `pip install dist/*.whl`
- [ ] Create git tag
- [ ] Push to trigger automated release

## Troubleshooting

### Common Issues

#### Build Fails
```bash
# Check for syntax errors
python -m py_compile src/quantum_simulator/*.py

# Check dependencies
pip check
```

#### Upload Fails
```bash
# Check package metadata
twine check dist/*

# Verify PyPI credentials
twine upload --repository testpypi dist/* --verbose
```

#### Documentation Build Fails
```bash
# Check MkDocs configuration
mkdocs build --verbose

# Verify all documentation links
mkdocs build --strict
```
