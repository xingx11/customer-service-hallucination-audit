# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog, and the project uses semantic versioning after the first release tag.

## [Unreleased]

### Added

- Stage-four release-readiness planning documents for final `v1.0.0` delivery closeout.
- Release checklist covering documentation review, local quality gates, CLI smoke tests, packaged data checks, PR review, and tagging steps.

### Changed

- Updated README, SPEC, development docs, and active task pointers to make stage four the current release-readiness phase.

## [0.3.0] - 2026-07-10

### Added

- Stage-three planning documents for release metadata cleanup, detector adapter boundaries, mock detector coverage, and minimal opt-in LLM detector integration.
- Detector adapter contract so the pipeline can accept injected detectors while keeping the deterministic detector as the default.
- Deterministic and mock detector adapters with CLI selection via `--detector deterministic|mock`.
- LLM prompt template, JSON output schema, and offline parser validation for converting structured model output to `DetectionResult`.
- Optional `llm` detector selection backed by environment-only OpenAI-compatible configuration and offline fake-client tests.
- Stage-three Markdown and JSON delivery reports under `docs/reports/`.

### Changed

- Updated README, SPEC, development docs, and active task pointers to make stage three the final feature phase before `v1.0.0` delivery closeout.
- Released package and CLI version metadata as `0.3.0`.

## [0.2.0] - 2026-07-10

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
