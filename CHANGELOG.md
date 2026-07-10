# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog, and the project uses semantic versioning after the first release tag.

## [Unreleased]

### Added

- Stage-two planning documents for robustness fixtures, rule explainability, per-type metrics, and report enhancements.
- Stage-two robustness fixtures covering rewritten prompts, difficult negatives, omissions, and safety-sensitive cases.
- Structured rule metadata with stable rule IDs, hallucination types, risk levels, descriptions, and trigger intent.
- Rule hit summaries in Markdown and JSON reports.
- Per-type metrics for label count, predicted count, true positive count, and mismatch count.
- Stage-two Markdown and JSON delivery reports under `docs/reports/`.

### Changed

- Expanded Markdown and JSON reports with type performance, high-risk case rationale, and clearer limitations.
- Updated README, SPEC, and development docs to reflect stage-two completion and offline reproducibility boundaries.

## [0.1.0] - 2026-07-10

### Added

- Project scaffold for an offline customer service hallucination audit pipeline.
- Python CLI package skeleton with linting, type checking, tests, and CI.
- Task 0110 source data under `data/`.
- End-to-end CLI pipeline that reads the default dataset and writes Markdown/JSON reports.
- Committed stage-one Markdown and JSON delivery reports under `docs/reports/`.
- CLI entrypoint tests covering help output, default packaged data, explicit paths, output files, and invalid input handling.

### Changed

- Synchronized stage-one plan, task checklist, SPEC, README, and development documentation to reflect first-phase completion.
