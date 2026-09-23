# Instructions for AI coding assistants (Claude Code, Copilot, GitLab Duo, Cursor ...)

Read by AI tools automatically. Copy to CLAUDE.md / .github/copilot-instructions.md if your tool needs that name.

## Definition of done - the pipeline will reject anything else
- Run `make lint` and `make coverage` before proposing a change. Both must pass.
- Every new or changed line of production code is covered by a unit test (gate: 80% on new lines).
- Tests assert behaviour. No test without an assertion; no tests that only call code to raise coverage.
- MR/PR title: `<type>(<scope>): <summary> <work item>` e.g. `feat(pricing): add bulk discount AB#12345`.

## Design rules
- Follow SOLID. New behaviour = new class implementing an existing interface (see `DiscountRule`),
  not new `if/elif` branches in an existing class.
- Inject dependencies through constructors; no hidden globals or service locators.
- Max cyclomatic complexity 8 per function (ruff C90 enforces it).
- Money is `Decimal`, never `float`.

## Never
- Add a dependency that is not available from the internal package proxy.
- Put secrets, tokens, hostnames or customer data in code, tests or fixtures.
- Edit the Makefile targets' report paths, `repo.yaml` kind, or pipeline files to get a change through.
