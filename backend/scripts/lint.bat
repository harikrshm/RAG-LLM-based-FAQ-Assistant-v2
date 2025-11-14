@echo off
REM Backend linting and formatting script for Windows

echo Running Black formatter...
black .

echo Running isort...
isort .

echo Running flake8 linter...
flake8 .

echo Linting complete!

