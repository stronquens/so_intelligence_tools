install-system-deps:
	./scripts/install-linux-deps.sh

install-python:
	poetry install

install-desktop:
	poetry run so-intelligence-tools install-linux-desktop-integration

bootstrap-linux:
	./scripts/install-linux-deps.sh
	poetry install
	poetry run so-intelligence-tools install-linux-desktop-integration
