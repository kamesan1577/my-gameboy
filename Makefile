REPO_DIR := $(shell pwd)
SERVICE_NAME := gpio-driver
SERVICE_FILE := /etc/systemd/system/$(SERVICE_NAME).service
AUTOSTART_DIR := $(HOME)/.config/autostart
AUTOSTART_FILE := $(AUTOSTART_DIR)/my-gameboy.desktop

.PHONY: install install-uv install-deps install-driver install-autostart \
        uninstall status logs help

## install: Run all install-* targets (full setup)
install: install-uv install-deps install-driver install-autostart
	@echo ""
	@echo "Setup complete. Reboot to launch automatically."

## install-uv: Install uv if not already installed
install-uv:
	@if command -v uv >/dev/null 2>&1; then \
		echo "uv is already installed: $$(uv --version)"; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "uv installed. You may need to restart your shell or source ~/.bashrc"; \
	fi

## install-deps: Install apt/pip dependencies and run uv sync
install-deps:
	@echo "Installing system packages..."
	sudo apt-get update -q
	sudo apt-get install -y python3-evdev
	@echo "Installing Python packages..."
	sudo pip install --break-system-packages gpiozero python-uinput
	@echo "Running uv sync..."
	cd $(REPO_DIR) && uv sync

## install-driver: Register and start gpio-driver systemd service
install-driver:
	@echo "Installing $(SERVICE_NAME) service..."
	sed 's|__REPO_DIR__|$(REPO_DIR)|g' \
		$(REPO_DIR)/systemd/gpio-driver.service.template \
		| sudo tee $(SERVICE_FILE) > /dev/null
	sudo systemctl daemon-reload
	sudo systemctl enable $(SERVICE_NAME)
	sudo systemctl restart $(SERVICE_NAME)
	@echo "$(SERVICE_NAME) service is active."

## install-autostart: Register launcher in desktop autostart
install-autostart:
	@echo "Installing desktop autostart entry..."
	mkdir -p $(AUTOSTART_DIR)
	sed 's|__REPO_DIR__|$(REPO_DIR)|g' \
		$(REPO_DIR)/systemd/my-gameboy.desktop.template \
		> $(AUTOSTART_FILE)
	@echo "Autostart entry written to $(AUTOSTART_FILE)"

## uninstall: Remove all installed services and autostart entries
uninstall:
	@echo "Removing $(SERVICE_NAME) service..."
	-sudo systemctl stop $(SERVICE_NAME)
	-sudo systemctl disable $(SERVICE_NAME)
	-sudo rm -f $(SERVICE_FILE)
	-sudo systemctl daemon-reload
	@echo "Removing autostart entry..."
	-rm -f $(AUTOSTART_FILE)
	@echo "Uninstall complete."

## status: Show gpio-driver service status
status:
	systemctl status $(SERVICE_NAME)

## logs: Stream gpio-driver service logs
logs:
	journalctl -fu $(SERVICE_NAME)

## help: Show this help message
help:
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^## [a-zA-Z_-]+:' $(MAKEFILE_LIST) \
		| sed 's/^## //' \
		| awk -F': ' '{printf "  \033[36m%-22s\033[0m%s\n", $$1, $$2}'
