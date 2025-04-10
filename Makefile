.PHONY: setup dev test lint clean venv

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

setup: venv
	cp -n .env.example .env || true

dev:
	@echo "Starting development environment..."
	$(PYTHON) scripts/dev.py

test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest --cov=agents --cov=shared tests/

lint:
	$(PYTHON) -m black agents/ shared/ scripts/ tests/
	$(PYTHON) -m isort agents/ shared/ scripts/ tests/
	$(PYTHON) -m flake8 agents/ shared/ scripts/ tests/

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

.env.example:
	@echo "Creating .env.example file..."
	@echo "# API Keys" > .env.example
	@echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env.example
	@echo "# Configuration" >> .env.example
	@echo "LOG_LEVEL=INFO" >> .env.example
	@echo "VECTOR_DB_PATH=./data/vector_db" >> .env.example

# Create .env.example if it doesn't exist
setup-env: .env.example
