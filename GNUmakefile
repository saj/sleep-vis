DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


.PHONY: all
all:
	$(MAKE) lint
	$(MAKE) test


.PHONY: lint
lint:
	pylint '$(DIR)/_lib'
	@find '$(DIR)' -mindepth 1 -maxdepth 1 -type f -perm +0111 -print0 \
		| xargs -0t -n 1 pylint


.PHONY: test
test:
	@find '$(DIR)/_lib' -type f -name '*.py' -print0 \
		| PYTHONPATH='$(DIR)' xargs -0t -n 1 -J % python3 % --doctest
	@find '$(DIR)' -mindepth 1 -maxdepth 1 -type f -perm +0111 -print0 \
		| PYTHONPATH='$(DIR)' xargs -0t -n 1 -J % python3 % --doctest
