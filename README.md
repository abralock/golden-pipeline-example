# Golden Pipeline example: one quality standard for GitLab + Azure DevOps

```
ci-templates/                 <- owned by the PLATFORM team (one repo, versioned with tags)
  scripts/                    <- the actual gate logic, shared by both CI systems
    detect-profile.sh         code | iac | scripts | config  (+ blocks "declare iac to skip tests")
    check-contract.sh         Makefile must have setup/lint/test/coverage/build WITH recipes
    lint-title.sh             MR/PR title = conventional commit + work item (AB#123 / PAY-123)
    static-lint.sh            ALL repos: gitleaks, shellcheck, yamllint, checkov
    quality_gate.py           tests > 0, 0 failures, overall floor, 80% on NEW lines (diff-cover)
    releaserc.*.json          semantic-release config (version tags from commit titles)
  toolbox/Dockerfile          image containing all of the above, pushed to both registries
  templates/golden-pipeline.yml   GitLab CI/CD component
  azure/golden-pipeline.yml       Azure Pipelines extends-template
  contract/Makefile.{java,dotnet,node}  starters for other stacks
  policies/                   GitLab pipeline execution policy (phase-3 enforcement)

sample-service/               <- what a TEAM owns (Python example)
  Makefile  repo.yaml  .gitlab-ci.yml  azure-pipelines.yml  AGENTS.md  CODEOWNERS
sample-iac/                   <- Terraform + shell only: no coverage gate, still scanned
```

## Pipeline flow

| Stage | Job | Runs for | Blocks when |
|---|---|---|---|
| validate | detect-profile | all | repo.yaml says iac/scripts but build files exist |
| validate | mr-title | MR/PR | title lacks `type(scope): ...` or work item |
| validate | static-lint | all | secret found, shellcheck/yamllint/checkov fail |
| validate | contract | code | Makefile target missing or recipe-less |
| test | unit-test | code | `make setup && make lint && make coverage` fails |
| quality | quality-gate | code | 0 tests, failures, below overall floor, **< 80% on new lines** |
| build | build | code, main only | `make build` fails |
| release | release | main only | creates tag vX.Y.Z from commit titles |
| deploy | team stages | main only | platform forces the condition; teams can't bypass |

## Tested locally (in this package)

- Contract check passes/fails correctly (including a `.PHONY`-only target trick).
- Python sample: lint → 6 tests → 100% coverage → gate PASS → wheel built.
- MR adding untested `CouponDiscount`: overall 87.8% (would pass an overall rule) but new code 37% → **FAIL**. After adding a test → PASS.
- Failing test → FAIL. JaCoCo XML parsed. `QG_MODE=warn` → reports but exit 0.
- Title lint: 2 valid / 3 invalid titles behave as expected.
- IaC repo: profile `iac`, checkov found 7 issues → 4 fixed, 3 justified with inline `#checkov:skip` → PASS. Planted token → gitleaks FAIL.
- All YAML passes yamllint, all scripts pass shellcheck.

## Not tested here (validate in your environment)

- The toolbox Docker build (no Docker daemon in the sandbox).
- GitLab component + Azure template on real runners/agents. Run GitLab "CI Lint" and an Azure
  "Validate" on a pilot project first, and check field names against your GitLab/Azure versions
  (especially the pipeline execution policy, which requires GitLab Ultimate).
- semantic-release on Azure Repos: Build Service identity needs Contribute + Create tag.

## Platform settings (outside YAML)

**GitLab** – squash-merge on MRs, "Pipelines must succeed", MR approvals + CODEOWNERS,
protected `main`, protected environments; later: compliance framework + pipeline execution policy.

**Azure DevOps** – on `main`: require PR, squash merge only, build validation (this pipeline),
"Check for linked work items", required reviewers + auto-include code owners.
On prod environments: Approvals + **Required template** check → `Platform/ci-templates`
`azure/golden-pipeline.yml`.
