.PHONY: all test clean

build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf build dist

test:
	pytest --cov-branch --cov-report=xml --cov=. test/test.py

all: test build publish clean
