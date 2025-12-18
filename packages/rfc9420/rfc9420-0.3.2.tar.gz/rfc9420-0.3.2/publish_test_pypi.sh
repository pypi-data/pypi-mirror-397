#!/bin/bash
# Script to publish RFC9420 to test PyPI using uv
# 
# Prerequisites:
# 1. Create an account at https://test.pypi.org/account/register/
# 2. Generate an API token at https://test.pypi.org/manage/account/token/
# 3. Set the token as an environment variable: export TEST_PYPI_TOKEN="your-token"
#
# Usage:
#   ./publish_test_pypi.sh
#   TEST_PYPI_TOKEN="your-token" ./publish_test_pypi.sh

set -e

TOKEN="${TEST_PYPI_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "Error: Test PyPI token not provided."
    echo "Either set TEST_PYPI_TOKEN environment variable or pass it as an argument"
    echo ""
    echo "To get a token:"
    echo "1. Create account at https://test.pypi.org/account/register/"
    echo "2. Generate token at https://test.pypi.org/manage/account/token/"
    exit 1
fi

echo "Building package..."
uv build

echo "Publishing to test PyPI..."
uv publish --publish-url https://test.pypi.org/legacy/ --token "$TOKEN"

echo ""
echo "Successfully published to test PyPI!"
echo "Install with: pip install -i https://test.pypi.org/simple/ rfc9420"

