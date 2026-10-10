# Contributing

How to make changes to this repository.

## Setup

Follow [docs/development.md](docs/development.md) to learn how to add skills and run the checks.

## Branching

- Start every change on a feature branch created from an up-to-date `main`.
- Never push directly to `main`. Every change reaches `main` through a pull request.

## Making a Change

1. Create a feature branch from `main`.
2. Make and commit your changes.
3. Run the checks (see [docs/development.md](docs/development.md)), including `python tools/run_snippets.py --demo` for any skill whose code changed.
4. Update [docs/verification.md](docs/verification.md) if you tested on hardware.
5. Push your branch and open a pull request into `main`.

## Pull Requests

- Give it a clear and concise title that describes the change.
- Fill in the description using [.github/pull_request_template.md](.github/pull_request_template.md).
- Ensure all CI checks pass.
- A maintainer must review and approve the pull request before merging.

## Skill Principles

- One task per skill. Only critical information, exact commands, and exact code.
- Link to Digilent's documentation instead of restating it.
- Do not add Digilent hardware or company knowledge; the skills wrap the SDK.
- Never include code that has not been run (on a demo device at minimum).

## Releases and Tags

Releases are created from version tags on `main`.

- Use the format `vMAJOR.MINOR.PATCH` (e.g. `v1.0.0`) following [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
- Bump the `version` in `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json` only when releasing.
- Only maintainers create release tags, and only after the tagged commit has passed CI and been reviewed.
