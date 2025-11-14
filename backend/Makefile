.PHONY: format lint lint-fix check test install

# Format code with black and isort
format:
	black .
	isort .

# Check formatting without making changes
format-check:
	black --check .
	isort --check .

# Run flake8 linter
lint:
	flake8 .

# Run linter and auto-fix what can be fixed
lint-fix:
	black .
	isort .
	flake8 .

# Run all checks
check: format-check lint
	@echo "All checks passed!"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	pytest

