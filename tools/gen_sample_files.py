#!/usr/bin/env python3
"""Generate the per-repo boilerplate for every sample so they stay consistent.

Run from the repo root:  python3 tools/gen_sample_files.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "samples"
GL_REG = "registry.corp.example/platform"
AZ_REG = "corpacr.azurecr.io/platform"

SAMPLES = {
    "python-service": dict(lang="python", image="build-python:3.12", fmt="cobertura", team="team-pricing-py",
        rules=["Money is `Decimal`, never `float`.",
               "Type hints on all public functions.",
               "Max cyclomatic complexity 8 per function (ruff C90)."]),
    "go-service": dict(lang="go", image="build-go:1.24", fmt="cobertura", team="team-pricing-go",
        rules=["Money is `int64` cents, never `float64`.",
               "Return errors, don't panic in library code; wrap with `fmt.Errorf(\"...: %w\", err)`.",
               "Keep `main` thin: logic in a testable `run()`; code must pass `gofmt` and `go vet`."]),
    "java-maven-service": dict(lang="java", image="build-java-maven:17", fmt="jacoco", team="team-pricing-java",
        rules=["Money is `BigDecimal`, never `double`.",
               "Constructor injection only; no static singletons or service locators.",
               "Max cyclomatic complexity 8 per method (Checkstyle, config/checkstyle.xml)."]),
    "java-gradle-service": dict(lang="java", image="build-java-gradle:21", fmt="jacoco", team="team-pricing-java",
        rules=["Money is `BigDecimal`, never `double`.",
               "Constructor injection only; no static singletons or service locators.",
               "Max cyclomatic complexity 8 per method (Checkstyle, config/checkstyle.xml)."]),
    "node-ts-service": dict(lang="typescript", image="build-node:22", fmt="cobertura", team="team-pricing-node",
        rules=["TypeScript `strict` mode; no `any`.",
               "Money is integer cents (`number` of cents) or a decimal library, never floating-point currency.",
               "Max cyclomatic complexity 8 per function (ESLint `complexity`)."]),
    "nextjs-app": dict(lang="typescript", image="build-node:22", fmt="cobertura", team="team-storefront",
        rules=["Business logic lives in `lib/`, not in page or layout components.",
               "Components are tested with Testing Library by behaviour (what the user sees), not implementation.",
               "TypeScript `strict`; no `any`; max complexity 8 (ESLint `complexity`).",
               "Validate all input in route handlers and server actions."]),
}

AGENTS = """# Instructions for AI coding assistants (Claude Code, Copilot, GitLab Duo, Cursor ...)

AI tools read this file automatically. Copy it to CLAUDE.md or .github/copilot-instructions.md if your tool needs that name.

## Definition of done: the pipeline will reject anything else
- Run `make lint` and `make coverage` before proposing a change. Both must pass.
- Every new or changed line of production code is covered by a unit test (checked: 80% of new lines).
- Tests assert behaviour. Don't write a test without an assertion, or tests that only call code to raise coverage.
- MR/PR title: `<type>(<scope>): <summary> <work item>`, e.g. `feat(pricing): add bulk discount AB#12345`.

## Design rules (SOLID)
- New behaviour = a new type implementing an existing interface, not new if/else branches in an existing class.
- Depend on abstractions; inject dependencies through constructors or parameters.
{lang_rules}

## Never
- Add a dependency that is not available from the internal package proxy.
- Put secrets, tokens, hostnames or customer data in code, tests or fixtures.
- Edit Makefile report paths, coverage exclusions, `repo.yaml` kind or pipeline files to get a change through.
"""

GITLAB = """# Everything a team writes on GitLab. The checks live in the platform component.
include:
  - component: $CI_SERVER_FQDN/platform/ci-templates/golden-pipeline@1.0.0
    inputs:
      build_image: {gl_reg}/{image}
{fmt_line}      min_overall_coverage: 80     # new service: 80% from day one (legacy repos: start at today's number)

# Team-owned deploy job. Protected environments are configured in GitLab settings.
deploy-dev:
  stage: release
  needs: [qg:build]
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  environment: dev
  script:
    - echo "deploy dist/ to dev"
"""

AZURE = """# Everything a team writes on Azure DevOps. The checks live in the platform template.
# PR builds are triggered by the branch policy "Build validation", not by a pr: block.
trigger:
  branches:
    include: [main]

resources:
  repositories:
    - repository: templates
      type: git
      name: Platform/ci-templates
      ref: refs/tags/v1.0.0        # pin a version; the platform ships upgrades as new tags

extends:
  template: azure/golden-pipeline.yml@templates
  parameters:
    buildImage: {az_reg}/{image}
    minOverallCoverage: 80
    deployStages:
      - stage: DeployDev
        jobs:
          - deployment: Deploy
            environment: {name}-dev
            strategy:
              runOnce:
                deploy:
                  steps:
                    - script: echo "deploy to dev"
      - stage: DeployProd
        dependsOn: DeployDev
        jobs:
          - deployment: Deploy
            environment: {name}-prod    # has Approvals + "Required template" checks
            strategy:
              runOnce:
                deploy:
                  steps:
                    - script: echo "deploy to prod"
"""

REPO_YAML = """# Repo metadata read by the platform (inventory, dashboards, gate profile).
kind: service        # service | library | iac | scripts | config
owner: {team}
tier: 1              # 1 = customer-facing prod, 2 = internal, 3 = tooling
language: {lang}
work_items: azure-boards   # azure-boards | jira
"""

CODEOWNERS = """# Human approval is still required; AI review is a first pass only.
*                     @{team}
# The platform team must approve changes that could weaken the checks.
/Makefile             @platform/architects
/repo.yaml            @platform/architects
/.gitlab-ci.yml       @platform/architects
/azure-pipelines.yml  @platform/architects
{extra}"""

EXTRA_OWNERS = {
    "node-ts-service": "/jest.config.js       @platform/architects   # coverage exclusions\n",
    "nextjs-app": "/jest.config.js       @platform/architects   # coverage exclusions\n",
    "java-maven-service": "/config/checkstyle.xml @platform/architects\n",
    "java-gradle-service": "/config/checkstyle.xml @platform/architects\n",
}

for name, s in SAMPLES.items():
    d = ROOT / name
    d.mkdir(parents=True, exist_ok=True)
    fmt_line = f"      coverage_format: {s['fmt']}\n" if s["fmt"] != "cobertura" else ""
    (d / "AGENTS.md").write_text(AGENTS.format(lang_rules="\n".join(f"- {r}" for r in s["rules"])))
    (d / ".gitlab-ci.yml").write_text(GITLAB.format(gl_reg=GL_REG, image=s["image"], fmt_line=fmt_line))
    (d / "azure-pipelines.yml").write_text(AZURE.format(az_reg=AZ_REG, image=s["image"], name=name))
    (d / "repo.yaml").write_text(REPO_YAML.format(team=s["team"], lang=s["lang"]))
    (d / "CODEOWNERS").write_text(CODEOWNERS.format(team=s["team"], extra=EXTRA_OWNERS.get(name, "")))
    print("generated", name)
