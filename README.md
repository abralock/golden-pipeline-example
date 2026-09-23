# Golden Pipeline example: one quality standard for GitLab + Azure DevOps

Stacks covered: **Go · Python · Java (Maven + Gradle, JDK 17/21) · .NET (C#) · TypeScript / Node.js · Next.js · Angular**, plus YAML/shell/Terraform-only repos.

Full explanation: [`docs/golden-pipeline-explained.md`](docs/golden-pipeline-explained.md)

```
ci-templates/                     <- owned by the PLATFORM team (one repo, versioned with tags)
  scripts/                        <- the actual check logic, shared by both CI systems
    detect-profile.sh             code | iac | scripts | config  (+ blocks "declare iac to skip tests")
    check-contract.sh             Makefile must have setup/lint/test/coverage/build WITH recipes
    lint-title.sh                 MR/PR title = conventional commit + work item (AB#123 / PAY-123)
    static-lint.sh                ALL repos: gitleaks, shellcheck, yamllint, checkov
    quality_gate.py               tests > 0, 0 failures, overall floor, report paths valid,
                                  changed files present in report, 80% on NEW lines
    releaserc.*.json              semantic-release config (version tags from commit titles)
  toolbox/Dockerfile              image containing all of the above, pushed to both registries
  templates/golden-pipeline.yml   GitLab CI/CD component
  azure/golden-pipeline.yml       Azure Pipelines extends-template
  contract/Makefile.<stack>       starters: go, python, maven, gradle, dotnet, node-ts, nextjs, angular
  policies/                       GitLab pipeline execution policy (phase-3 enforcement)

samples/                          <- what a TEAM owns; each passes the checks
  go-service/                     Go 1.24          go test + go-junit-report + gocover-cobertura
  python-service/                 Python 3.12      pytest + pytest-cov + ruff
  java-maven-service/             Java 17, Maven   JUnit 5 + JaCoCo + Checkstyle
  java-gradle-service/            Java 21, Gradle  JUnit 5 + JaCoCo + Checkstyle
  dotnet-service/                 .NET 8, C#       xUnit + coverlet + ReportGenerator + CA1502
  node-ts-service/                Node 22, TS      Jest + ts-jest + ESLint
  nextjs-app/                     Next.js 16       Jest (next/jest) + Testing Library + ESLint
  angular-app/                    Angular 21       Vitest (ng test) + angular-eslint
  iac-terraform/                  Terraform+shell  no coverage check; still scanned

tools/gen_sample_files.py         regenerates repo.yaml / pipelines / AGENTS.md / CODEOWNERS per sample
```

Each sample has the same team-owned files: `Makefile`, `repo.yaml`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `AGENTS.md`, `CODEOWNERS`.

## The Makefile contract, per stack

| Stack | `lint` | `coverage` → `reports/junit*.xml` | `coverage` → `reports/coverage.xml` |
|---|---|---|---|
| Go | gofmt, go vet (+ golangci-lint) | go-junit-report | gocover-cobertura (Cobertura) |
| Python | ruff (incl. complexity C90) | pytest `--junitxml` | pytest-cov (Cobertura) |
| Java / Maven | Checkstyle (complexity ≤ 8) | Surefire XML | JaCoCo |
| Java / Gradle | Checkstyle (complexity ≤ 8) | Gradle test XML | JaCoCo |
| .NET (C#) | `dotnet format` + build with warnings as errors, CA1502 (complexity ≤ 8) | JunitXml.TestLogger | coverlet → ReportGenerator merge (Cobertura) |
| TypeScript / Node | ESLint (complexity ≤ 8) + `tsc --noEmit` | jest-junit | Jest, V8 provider (Cobertura) |
| Next.js | ESLint (next config, complexity ≤ 8) + `tsc` | jest-junit | Jest via next/jest, V8 provider (Cobertura) |
| Angular | angular-eslint (complexity ≤ 8) + `tsc` | Vitest junit reporter | Vitest V8 via `ng test --coverage`, all app files included (Cobertura) |

Java teams set `coverage_format: jacoco` (GitLab). Different JDK versions only change `build_image`.

## Pipeline flow

| Stage | Job | Runs for | Blocks when |
|---|---|---|---|
| validate | detect-profile | all | repo.yaml says iac/scripts but build files exist |
| validate | mr-title | MR/PR | title lacks `type(scope): ...` or work item |
| validate | static-lint | all | secret found, shellcheck/yamllint/checkov fail |
| validate | contract | code | Makefile target missing or recipe-less |
| test | unit-test | code | `make setup && make lint && make coverage` fails |
| quality | quality-gate | code | 0 tests, failures, below overall floor, broken report paths, changed files missing from report, **< 80% on new lines** |
| build | build | code, main only | `make build` fails |
| release | release | main only | creates tag vX.Y.Z from commit titles |
| deploy | team stages | main only | the platform forces the condition; teams can't bypass |

## What was tested in the sandbox

| Sample | lint | tests | coverage | check | build | notes |
|---|---|---|---|---|---|---|
| go-service | ✅ | ✅ 10 | 83.9% | ✅ PASS | ✅ binary runs | MR with untested `Bulk()` → new code 0% → **blocked** |
| python-service | ✅ | ✅ 7 | 100% | ✅ PASS | ✅ wheel | MR with untested class: overall 87.8%, new 37% → **blocked** |
| node-ts-service | ✅ | ✅ 6 | 100% | ✅ PASS | ✅ dist/ | MR with untested class → new 20% → **blocked**; complexity 9 → ESLint error |
| nextjs-app | ✅ | ✅ 8 | 100% | ✅ PASS | ✅ standalone server serves page | |
| angular-app | ✅ | ✅ 9 | 100% | ✅ PASS | ✅ production bundle | MR with an untested new component → new 0% → **blocked** |
| dotnet-service | ✅ build, format, CA1502 | ⚠️ 6/6 via stub runner | – | Cobertura mapping ✅ | – | NuGet blocked in sandbox: library builds with warnings-as-errors; CA1502 fails a complexity-10 method; test code compiled and run against the real library with a stub xUnit |
| java-maven-service | ⚠️ | ⚠️ | – | JaCoCo parsing ✅ | – | Maven Central blocked in sandbox: sources + tests compiled (JDK 17), logic verified |
| java-gradle-service | ⚠️ | ⚠️ | – | JaCoCo parsing ✅ | – | `gradle compileJava` ✅ offline; tests need Maven Central |
| iac-terraform | ✅ | – | – | ✅ | – | checkov 7 findings → 4 fixed, 3 documented exceptions; planted secret caught |

Other checks: contract check (including a `.PHONY`-only trick), MR title lint, warn mode, profile dodge attempt,
yamllint on all YAML, shellcheck on all scripts.

**Found and fixed during testing (both let untested code pass silently):**

1. ts-jest + TypeScript 6: Jest's default (istanbul) coverage writes broken file paths, so the new-code
   check saw nothing. Fix: samples use `coverageProvider: "v8"`, and `quality_gate.py` **fails** if the
   report's paths don't match repo files.
2. Angular: the test build tree-shakes files no test imports, so a new untested component never appears
   in the report. Fix: the Angular starter uses `--coverage-include` for all app files, and
   `quality_gate.py` **fails** an MR whose changed source files are missing from the report (any language).
   Remaining limit: code that nothing imports at all (dead code) isn't measured in Angular.

## Not tested here (validate in your environment)

- Java and .NET builds end to end (need Maven Central / NuGet, i.e. your Artifactory/Nexus mirror).
  .NET test package versions were checked against upstream release tags; pin your approved versions.
- The toolbox Docker build (no Docker daemon in the sandbox).
- GitLab component + Azure template on real runners/agents: run GitLab "CI Lint" and an Azure
  "Validate" on a pilot project first; check the pipeline execution policy fields against your GitLab version.
- semantic-release on Azure Repos: Build Service identity needs Contribute + Create tag.
- Corporate package mirrors: set GOPROXY, Maven `settings.xml`, Gradle `distributionUrl`, `nuget.config`,
  npm/pip registries to Artifactory/Nexus in the build images.
- Angular 22 (needs Node ≥ 22.22.3); the sample uses Angular 21 because the sandbox has Node 22.22.2.

## Platform settings (outside YAML)

**GitLab**: squash-merge on MRs, "Pipelines must succeed", MR approvals + CODEOWNERS,
protected `main`, protected environments; later, a compliance framework + pipeline execution policy.

**Azure DevOps**: on `main`, require PR, squash merge only, build validation (this pipeline),
"Check for linked work items", required reviewers + auto-include code owners.
On prod environments: Approvals + **Required template** check → `Platform/ci-templates`
`azure/golden-pipeline.yml`.
