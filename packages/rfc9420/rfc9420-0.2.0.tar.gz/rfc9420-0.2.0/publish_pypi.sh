#!/bin/bash
# Script to publish PyMLS to production PyPI using uv
# 
# Prerequisites:
# 1. Create an account at https://pypi.org/account/register/
# 2. Generate an API token at https://pypi.org/manage/account/token/
# 3. Set the token as an environment variable: export PYPI_TOKEN="your-token"
#
# Usage:
#   ./publish_pypi.sh
#   PYPI_TOKEN="your-token" ./publish_pypi.sh

set -e

TOKEN="${PYPI_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "Error: PyPI token not provided."
    echo "Either set PYPI_TOKEN environment variable or pass it as an argument"
    echo ""
    echo "To get a token:"
    echo "1. Create account at https://pypi.org/account/register/"
    echo "2. Generate token at https://pypi.org/manage/account/token/"
    exit 1
fi

echo "Building package..."
uv build

echo "Publishing to PyPI..."
# For production PyPI, you can either:
# 1. Omit --publish-url (defaults to production)
# 2. Explicitly use: --publish-url https://upload.pypi.org/legacy/
uv publish --token "$TOKEN"

echo ""
echo "Successfully published to PyPI!"
echo "Install with: pip install PyMls"
echo "View at: https://pypi.org/project/PyMls/"

