#!/bin/bash

## Intrepid AI Python SDK Building - Publishing

## Build Python package with poetry
## and publish to Pypi if requested
## (via --publish)


# Enable exit on error
set -e

# Step 1: Build the package
echo "Building the package..."
poetry build
echo "\nBuild completed successfully."

# Step 2: Install the package using Poetry
echo "Installing the package..."
poetry install
echo "\nInstallation completed successfully."

# Step 3: If --publish flag is provided, upload the package
if [[ "$1" == "--publish" ]]; then
    echo "\nPublishing the package..."
    # Check if twine is installed
    if ! command -v twine &> /dev/null; then
        echo "Error: twine is not installed. Please install it first."
        exit 1
    fi
    twine upload dist/*
    echo "\nPackage published successfully."
fi
