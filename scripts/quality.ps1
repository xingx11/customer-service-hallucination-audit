$ErrorActionPreference = "Stop"

python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
