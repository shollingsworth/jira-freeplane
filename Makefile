.DEFAULT_GOAL := help

COMMIT_HASH := $(shell git rev-parse HEAD)
VERSION := $(shell git describe --tags --always)

help: show_ver
	@echo ""
	@echo "Available commands:"
	@cat Makefile | grep '^\w' \
		| grep -v ' := ' \
		| cut -d ':' -f 1 | grep -v '^help$$'

clean:
	rm -rfv dist/*

show_ver:
	@echo "VERSION: $(VERSION)"
	@echo "COMMIT_HASH: $(COMMIT_HASH)"

test: clean show_ver
	poetry build
	docker build -t jira-freeplane-test:$(VERSION) -f docker/test.Dockerfile .
	docker run --rm -it -v $(pwd):/app jira-freeplane-test:$(VERSION) bash
