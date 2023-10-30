all: setup format mypy pylint

.PHONY: setup
setup:
	@echo "Current version: $(shell ./get-version.sh)"
	poetry install

.PHONY: format
format:
	poetry run isort .
	poetry run autopep8 -r --in-place .

.PHONY: test
test: setup
	mkdir -p test_output/album
	poetry run python3 -m camptown -vvv test/album/album.json test_output/album

.PHONY: pylint
pylint:
	poetry run pylint camptown

.PHONY: mypy
mypy:
	poetry run mypy -p camptown --ignore-missing-imports --check-untyped-defs

.PHONY: preflight
preflight:
	@echo "Checking commit status..."
	@git status --porcelain | grep -q . \
		&& echo "You have uncommitted changes" 1>&2 \
		&& exit 1 || exit 0
	@echo "Checking branch..."
	@[ "$(shell git rev-parse --abbrev-ref HEAD)" != "main" ] \
		&& echo "Can only build from main" 1>&2 \
		&& exit 1 || exit 0
	@echo "Checking upstream..."
	@git fetch \
		&& [ "$(shell git rev-parse main)" != "$(shell git rev-parse main@{upstream})" ] \
		&& echo "main branch differs from upstream" 1>&2 \
		&& exit 1 || exit 0

.PHONY: build
build: setup preflight pylint
	poetry build

.PHONY: clean
clean:
	rm -rf dist .mypy_cache .pytest_cache .coverage
	find . -name __pycache__ -print0 | xargs -0 rm -r

.PHONY: upload
upload: clean test build
	poetry publish

.PHONY: doc
doc:
	poetry run sphinx-build -b html docs/ docs/_build -D html_theme=alabaster

