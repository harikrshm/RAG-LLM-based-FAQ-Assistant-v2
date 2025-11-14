#!/bin/bash

# Backend linting and formatting script

echo "Running Black formatter..."
black .

echo "Running isort..."
isort .

echo "Running flake8 linter..."
flake8 .

echo "Linting complete!"

