REQUIREMENTS = requirements.txt
PYTHON = python3

MYPY_FLAGS = --warn-return-any \
			 --warn-unused-ignores \
			 --ignore-missing-imports \
			 --disallow-untyped-defs \
			 --check-untyped-defs

install:
	pip install -r $(REQUIREMENTS)

run:
	$(PYTHON) a_maze_ing.py

debug:
	$(PYTHON) -m pdb a_maze_ing.py

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "\n=== Arquivos apagados com sucesso! ===\n"

lint:
	-$(PYTHON) -m flake8
	-$(PYTHON) -m mypy $(MYPY_FLAGS) .

lint-strict:
	-$(PYTHON) -m flake8
	-$(PYTHON) -m mypy --strict .