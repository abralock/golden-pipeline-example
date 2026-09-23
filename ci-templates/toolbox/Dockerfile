# Platform "toolbox" image: every gate tool, versions pinned, owned by the platform team.
# Build from the ci-templates repo root:
#   docker build -f toolbox/Dockerfile -t ci-toolbox:1.0.0 .
# Push to BOTH registries, e.g.
#   registry.corp.example/platform/ci-toolbox:1.0.0   (GitLab)
#   corpacr.azurecr.io/platform/ci-toolbox:1.0.0       (Azure DevOps)
# Language SDKs are NOT in here - the unit-test job runs in the team's own build image.
# In an air-gapped network, point pip/npm/curl at your Artifactory/Nexus mirrors.

# semantic-release 24 needs Node >= 20 (Debian's apt nodejs is 18)
FROM node:22-bookworm-slim AS node

FROM python:3.12-slim-bookworm

ARG GITLEAKS_VERSION=8.21.2

RUN apt-get update && apt-get install -y --no-install-recommends \
        git make curl jq ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Node runtime only (don't overwrite python's /usr/local)
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN pip install --no-cache-dir \
        diff-cover==10.6.0 yamllint==1.35.1 shellcheck-py==0.10.0.1 checkov==3.3.19

RUN curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
      | tar -xz -C /usr/local/bin gitleaks

RUN npm install -g semantic-release@24 @semantic-release/gitlab@13 \
        conventional-changelog-conventionalcommits@8

COPY scripts/ /opt/ci/
RUN chmod +x /opt/ci/*.sh /opt/ci/*.py
ENV PATH="/opt/ci:${PATH}"
