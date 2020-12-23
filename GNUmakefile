SHELL := bash

PYLINT_OPTS := --jobs=0 \
	--persistent=n --reports=n --score=n \
	--disable=invalid-name \
	--disable=missing-class-docstring \
	--disable=missing-function-docstring \
	--disable=missing-module-docstring

DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


all:
	$(MAKE) lint
	$(MAKE) test

.PHONY: all


lint:
	pylint $(PYLINT_OPTS) '$(DIR)/_lib'
	@find '$(DIR)' -mindepth 1 -maxdepth 1 -type f -perm +0111 -print0 \
		| xargs -0t -n 1 pylint $(PYLINT_OPTS)

.PHONY: lint


test:
	@find '$(DIR)/_lib' -type f -name '*.py' -print0 \
		| PYTHONPATH='$(DIR)' xargs -0t -n 1 -J % python3 % --doctest
	@find '$(DIR)' -mindepth 1 -maxdepth 1 -type f -perm +0111 -print0 \
		| PYTHONPATH='$(DIR)' xargs -0t -n 1 -J % python3 % --doctest

.PHONY: test
