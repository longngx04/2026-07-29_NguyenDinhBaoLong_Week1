SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: target-up target-down scan scan-opengrep normalize search analyze analyze-mock validate-analysis

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

validate-analysis:
	@python3 -c "from week3.validators import read_jsonl, validate_record_schema; records = read_jsonl('results/analysis/security-analysis.jsonl'); assert len(records) > 0; [validate_record_schema(r, 'schemas/security-analysis-record.schema.json') for r in records]; print(f'Validated {len(records)} analysis records successfully.')"
