#!/bin/bash

# Build script for CV Matcher

set -e

echo "Building CV Matcher..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Install build dependencies
echo "Installing build dependencies..."
pip install build twine

# Build package
echo "Building package..."
python -m build

# Check package
echo "Checking package..."
twine check dist/*

echo ""
echo "✓ Build complete!"
echo ""
echo "Built packages:"
ls -lh dist/

echo ""
echo "To publish to Test PyPI:"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To publish to PyPI:"
echo "  twine upload dist/*"
