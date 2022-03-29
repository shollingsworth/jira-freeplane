.DEFAULT_GOAL := help

COMMIT_HASH := $(shell git rev-parse HEAD)
VERSION := $(shell cat VERSION)

help:
	@echo ""
	@echo "Available commands:"
	@cat Makefile | grep '^\w' \
		| grep -v ' := ' \
		| cut -d ':' -f 1 | grep -v '^help$$'

build:
	@echo "VERSION: $(VERSION)"
	@echo "COMMIT_HASH: $(COMMIT_HASH)"
	docker build -t hollingsworthsteven/jira-freeplane:$(VERSION) .
	docker push hollingsworthsteven/jira-freeplane:$(VERSION)
