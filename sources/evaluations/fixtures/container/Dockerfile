# Container runtime for Codex substrate evaluations.
#
# Build from the repository root:
#   docker build -f sources/evaluations/fixtures/container/Dockerfile -t token-eval-codex:latest .
#
# The runner bind-mounts only the lane-required host toolchains, such as Codex,
# Node, Go, and the active treatment tool. This image supplies the OS userspace and common
# build/test dependencies so model-facing commands run inside a filesystem/process
# boundary rather than the controller host.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        coreutils \
        curl \
        file \
        git \
        jq \
        make \
        openssh-client \
        patch \
        procps \
        python3 \
        python3-venv \
        python3-dev \
        sqlite3 \
        build-essential \
        pkg-config \
        rsync \
        unzip \
        xz-utils \
        zstd \
    && rm -rf /var/lib/apt/lists/*

COPY sources/evaluations/fixtures/container/network-denied-shell.c /tmp/network-denied-shell.c
RUN cc -O2 -Wall -Wextra -Werror /tmp/network-denied-shell.c -o /usr/local/bin/eval-network-denied-shell \
    && mkdir -p /opt/data/model-network-bin \
    && ln -s /usr/local/bin/eval-network-denied-shell /opt/data/model-network-bin/bash \
    && rm /tmp/network-denied-shell.c

RUN useradd --create-home --shell /bin/bash eval \
    && mkdir -p /opt/data /workspace \
    && chown -R eval:eval /workspace

WORKDIR /workspace
USER eval
