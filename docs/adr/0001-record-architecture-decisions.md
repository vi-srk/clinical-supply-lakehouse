# ADR 0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

This project makes many design choices (platform, layering, orchestration, governance tooling). Reviewers and future maintainers need to know *why* each choice was made, not just what was built.

## Decision

Record every significant decision as a short ADR in `docs/adr/`, numbered in order, using the sections Context, Decision, Consequences and Alternatives considered.

## Consequences

- Trade-offs are explicit and reviewable in pull requests.
- A decision can be superseded by a later ADR without rewriting history.

## Alternatives considered

- **Wiki pages:** drift away from the code and are not versioned with it.
- **No records:** reasoning is lost; reviewers must guess.
