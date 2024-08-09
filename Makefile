build:
	python -m build

publish:
	twine upload dist/*
