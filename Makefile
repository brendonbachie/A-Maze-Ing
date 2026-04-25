all:

install:
	pip install -r requirements.txt
run:
	python main.py
debug:
	python -m pdb main.py
clean:
	rm -rf __pycache__ .mypy_cache