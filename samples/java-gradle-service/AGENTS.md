# Instructions for AI coding assistants (Claude Code, Copilot, GitLab Duo, Cursor ...)

AI tools read this file automatically. Copy it to CLAUDE.md or .github/copilot-instructions.md if your tool needs that name.

## Definition of done: the pipeline will reject anything else
- Run `make lint` and `make coverage` before proposing a change. Both must pass.
- Every new or changed line of production code is covered by a unit test (checked: 80% of new lines).
- Tests assert behaviour. Don't write a test without an assertion, or tests that only call code to raise coverage.
- MR/PR title: `<type>(<scope>): <summary> <work item>`, e.g. `feat(pricing): add bulk discount AB#12345`.

## Design rules (SOLID)
- New behaviour = a new type implementing an existing interface, not new if/else branches in an existing class.
- Depend on abstractions; inject dependencies through constructors or parameters.
- Money is `BigDecimal`, never `double`.
- Constructor injection only; no static singletons or service locators.
- Max cyclomatic complexity 8 per method (Checkstyle, config/checkstyle.xml).

## Never
- Add a dependency that is not available from the internal package proxy.
- Put secrets, tokens, hostnames or customer data in code, tests or fixtures.
- Edit Makefile report paths, coverage exclusions, `repo.yaml` kind or pipeline files to get a change through.
