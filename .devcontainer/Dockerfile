FROM mcr.microsoft.com/devcontainers/python:3.11-trixie

USER root

# Install Node.js from local pre-downloaded assets for both supported
# architectures. This keeps Node version pinned and avoids network downloads.
ARG NODE_VERSION=24.13.0
ARG TARGETARCH
COPY assets/node-v${NODE_VERSION}-linux-${TARGETARCH}.tar.gz /tmp/node.tar.gz

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates tar mc jq iputils-ping dnsutils postgresql-17 postgresql-17-pgvector redis-server prometheus \
    && if [ "${TARGETARCH}" != "amd64" ] && [ "${TARGETARCH}" != "arm64" ]; then \
         echo "Unsupported architecture for pinned Node asset: ${TARGETARCH}" >&2; \
         exit 1; \
       fi \
    && mkdir -p /usr/local/lib/nodejs \
    && tar -xzf /tmp/node.tar.gz -C /usr/local/lib/nodejs --strip-components=1 \
    && ln -sf /usr/local/lib/nodejs/bin/node /usr/local/bin/node \
    && ln -sf /usr/local/lib/nodejs/bin/npm /usr/local/bin/npm \
    && ln -sf /usr/local/lib/nodejs/bin/npx /usr/local/bin/npx \
    && rm -f /tmp/node.tar.gz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER vscode
