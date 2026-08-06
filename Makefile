SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: target-up target-down scan scan-opengrep normalize search analyze analyze-mock analyze-offline-full validate-analysis agent-test

agent-test:
	@LLM_PROVIDER=fake pytest -q tests/week3 2>/dev/null || LLM_PROVIDER=fake .venv/bin/pytest -q tests/week3

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

normalize:
	@python3 -m week2.normalize

search:
	@test -n "$(Q)" || (printf '%s\n' 'Usage: make search Q='\''SQL Injection'\''' >&2; exit 1)
	@python3 -m week2.search $(Q)

analyze:
	python3 -m week3.cli analyze \
	  --input results/normalized/findings.json \
	  --output results/analysis/security-analysis.jsonl \
	  --summary results/analysis/run-summary.json

analyze-mock:
	python3 -m week3.cli analyze \
	  --input fixtures/week3/valid-findings.json \
	  --provider fake \
	  --output results/analysis/security-analysis.jsonl \
	  --summary results/analysis/run-summary.json

analyze-offline-full:
	python3 -m week3.cli analyze \
	  --input results/normalized/findings.json \
	  --provider fake \
	  --output results/analysis/security-analysis.jsonl \
	  --summary results/analysis/run-summary.json

validate-analysis:
	@python3 -m week3.cli validate --input results/analysis/security-analysis.jsonl
