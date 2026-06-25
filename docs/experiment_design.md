# Experiment Design

## Research Question

Does runtime feedback improve LLM-based REST API test generation?

## Dataset

- Raw operations: 422
- Experiment operations: 208
- Pilot operations: 42
- Source: APIs.guru
- APIs: Spotify, SendGrid
- Sampling seed: 42

## Baseline

LLM-only:
- Input: OpenAPI operation
- Output: generated API test request
- No runtime feedback

## Proposed Method

LLM + Runtime Feedback:
- Generate initial test
- Execute request
- Collect status code, response body, error message
- Feed runtime feedback back to LLM
- Generate refined test

## Metrics

- Operation coverage
- Status code coverage
- Valid request rate
- 4xx coverage
- 5xx fault detection
- Unique error messages