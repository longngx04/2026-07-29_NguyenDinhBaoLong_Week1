FROM eclipse-temurin:23-jdk-noble

ARG OPENGREP_VERSION=1.26.0
ARG OPENGREP_URL=https://github.com/opengrep/opengrep/releases/download/v1.26.0/opengrep_manylinux_x86
ARG OPENGREP_SHA256=40c21299eeddabf743b856daa843d24f9d4a027130671cd45b3b21776fd9ab26
ARG FINDSECBUGS_VERSION=1.14.0
ARG FINDSECBUGS_URL=https://github.com/find-sec-bugs/find-sec-bugs/releases/download/version-1.14.0/findsecbugs-cli-1.14.0.zip
ARG FINDSECBUGS_SHA256=ff546e16e596ade5b6534a6da87881e569429bf46dfd8faed63ca63cdd69b4f8

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl jq unzip \
    && curl --fail --location --retry 3 --retry-all-errors --output /tmp/opengrep "$OPENGREP_URL" \
    && echo "$OPENGREP_SHA256  /tmp/opengrep" | sha256sum --check --status \
    && install --mode=0755 /tmp/opengrep /usr/local/bin/opengrep \
    && curl --fail --location --retry 3 --retry-all-errors --output /tmp/findsecbugs.zip "$FINDSECBUGS_URL" \
    && echo "$FINDSECBUGS_SHA256  /tmp/findsecbugs.zip" | sha256sum --check --status \
    && mkdir --parents /opt/findsecbugs \
    && unzip -q /tmp/findsecbugs.zip -d /opt/findsecbugs \
    && sed -i 's/\r$//' /opt/findsecbugs/findsecbugs.sh \
    && chmod 0755 /opt/findsecbugs/findsecbugs.sh \
    && ln -s /opt/findsecbugs/findsecbugs.sh /usr/local/bin/findsecbugs.sh \
    && rm -rf /var/lib/apt/lists/* /tmp/opengrep /tmp/findsecbugs.zip

WORKDIR /workspace
CMD ["bash"]
