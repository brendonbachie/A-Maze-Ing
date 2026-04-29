CONFIG = config.txt
REQUIREMENTS = "requirements.txt"
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	pip install -r $(requirements.txt)

run:
	python3 a_maze_ing.py

debug:
	python3 -m pdb a_maze_ing.py

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "\n===Arquivos apagados com sucesso!===\n"


lint:
	python3 -m flake8 
	python3 -m mypy .

lint-strict:
	python3 -m flake8
	python3 -m mypy --strict .