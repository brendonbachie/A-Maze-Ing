CONFIG = config.txt
REQUIREMENTS = "requirements.txt"
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	pip install -r $(requirements.txt)

run:
	python main.py

debug:
	python -m pdb main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +


lint:
	python3 -m flake8 --exclude . mlx
	python3 -m mypy .

lint-strict:
	-$(PYTHON) -m flake8 . --exclude $(VENV_NAME)
	-$(PYTHON) -m mypy . --strict