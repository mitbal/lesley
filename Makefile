build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf build dist

all: build publish clean
