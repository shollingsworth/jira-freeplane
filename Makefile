.DEFAULT_GOAL := help

COMMIT_HASH := $(shell git rev-parse HEAD)
VERSION := $(shell git describe --tags --always)

help: show_ver
	@echo ""
	@echo "Available commands:"
	@cat Makefile | grep '^\w' \
		| grep -v ' := ' \
		| cut -d ':' -f 1 | grep -v '^help$$'

show_ver:
	@echo "VERSION: $(VERSION)"
	@echo "COMMIT_HASH: $(COMMIT_HASH)"

build: show_ver
	docker build -t hollingsworthsteven/jira-freeplane:$(VERSION) .
	docker push hollingsworthsteven/jira-freeplane:$(VERSION)
