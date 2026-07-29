SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: target-up target-down scan scan-opengrep

target-up:
	@docker compose up --detach webgoat
	@for attempt in $$(seq 1 30); do \
		if curl --fail --silent --show-error http://127.0.0.1:8080/WebGoat/actuator/health >/dev/null; then \
			printf '%s\n' 'WebGoat is ready: http://127.0.0.1:8080/WebGoat/'; \
			exit 0; \
		fi; \
		sleep 2; \
	done; \
	docker compose logs --tail=100 webgoat; \
	printf '%s\n' 'WebGoat did not become healthy within 60 seconds.' >&2; \
	exit 1

target-down:
	@docker compose down

scan: scan-opengrep

scan-opengrep:
	@./scripts/scan-opengrep.sh
