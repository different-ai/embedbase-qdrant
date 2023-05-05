VERSION="$(shell python3 -c 'import toml; print(toml.load("pyproject.toml")["tool"]["poetry"]["version"])')"

#* Release

release: ## [Local development] Release a new version of the API.
	@echo "Releasing version ${VERSION}"; \
	read -p "Commit content:" COMMIT; \
	git add .; \
	echo "Committing '${VERSION}: $$COMMIT'"; \
	git commit -m "Release ${VERSION}: $$COMMIT"; \
	git push origin main
	@echo "Done, check '\033[0;31mhttps://github.com/different-ai/embedbase-qdrant/actions\033[0m'"

#* Testing

test: ## [Local development] Run all Python tests with pytest.
	docker-compose up -d
	while ! curl -s localhost:6333 > /dev/null; do sleep 1; done
	poetry run pytest test_hard.py; docker-compose down
	@echo "Done testing"

#* Installation
.PHONY: install
install:
	poetry lock -n
	poetry install -n
	

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py38-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run darglint --verbosity 2 embedbase-qdrant tests

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml ./

.PHONY: lint
lint: test check-codestyle mypy check-safety

.PHONY: help

help: # Run `make help` to get help on the make commands
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
