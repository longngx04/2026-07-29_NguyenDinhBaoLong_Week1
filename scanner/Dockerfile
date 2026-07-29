FROM ubuntu:24.04

# Binary is fetched by scripts/scan-opengrep.sh before `docker compose build`
# when missing locally; checksum is verified there against OPENGREP_SHA256.
COPY opengrep /usr/local/bin/opengrep

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl jq \
    && chmod 0755 /usr/local/bin/opengrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
CMD ["bash"]
