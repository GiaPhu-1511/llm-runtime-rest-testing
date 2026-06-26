# LLM Runtime REST Testing

Python research project for evaluating LLM-generated REST API tests from OpenAPI specifications, then improving those tests with runtime execution feedback.

The current experiment focuses on two research questions:

- RQ1: Endpoint Coverage
- RQ2: Fault Detection

## Project Overview

This project builds a pilot dataset of REST API operations, asks an LLM to generate executable API tests, runs those tests against live API endpoints, uses the runtime results to build feedback prompts, generates refined tests, and reports research-oriented metrics.

This project uses a local LLM through Ollama with `qwen2.5:7b`.

Gemini and OpenAI adapters were removed to keep the reported experiment reproducible and independent of API quota/cost limits.

## Architecture

The project is organized as a small pipeline:

1. Collect and extract OpenAPI operations.
2. Sample experiment and pilot datasets.
3. Generate baseline tests from pilot operations.
4. Execute baseline tests.
5. Build runtime feedback prompts.
6. Generate refined tests from feedback.
7. Execute refined tests.
8. Compute metrics and fault candidates.

Core modules:

- `src/pipeline/run_baseline.py`: baseline test generation.
- `src/executor.py`: HTTP execution engine for generated tests.
- `src/feedback/feedback_builder.py`: runtime feedback prompt construction.
- `src/feedback/run_feedback.py`: refined test generation.
- `src/feedback/execute_feedback.py`: refined test execution.
- `src/metrics.py`: RQ1/RQ2 metric reporting.

## Folder Structure

```text
config/
  experiment.yaml
datasets/
  openapi/
  raw/
  pilot/
  ground_truth/
outputs/
  baseline/
  feedback/
prompts/
src/
  collector/
  feedback/
  llm/
  pipeline/
tests/
```

## Requirements

- Python 3.11 or newer
- Ollama installed locally
- A pulled Ollama model, currently `qwen2.5:7b`
- Python dependencies from `requirements.txt`

The project uses live HTTP calls during execution, so network access is required when running test execution steps.

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Reproducibility

This repository contains all components required to reproduce the pilot experiment:

- OpenAPI collection scripts
- Operation extraction scripts
- Dataset sampling scripts
- Baseline generation pipeline
- Runtime feedback pipeline
- Evaluation metrics

Running the dataset preparation and experiment pipeline in sequence reproduces the reported pilot results.

## Ollama Setup

Install Ollama, then pull the configured model:

```bash
ollama pull qwen2.5:7b
```

Verify the model is available:

```bash
ollama list
```

The Ollama client is implemented in:

```text
src/llm/ollama_client.py
```

## Configuration

Experiment configuration lives in:

```text
config/experiment.yaml
```

Current LLM configuration:

```yaml
llm:
  provider: ollama
  model: qwen2.5:7b
  temperature: 0.0
  max_output_tokens: 2048
```

API base URLs are also configured in `config/experiment.yaml`.

## Dataset Preparation

Dataset preparation scripts are in `src/collector/`.

Collect OpenAPI specs:

```bash
python -m src.collector.collect_openapi
```

Extract operations:

```bash
python -m src.collector.extract_operations
```

Sample experiment and pilot operations:

```bash
python -m src.collector.sample_operations
```

The current pilot dataset is:

```text
datasets/pilot/pilot_operations.csv
```

## Experiment Pipeline

Run the full experiment in this order:

```bash
python -m src.pipeline.run_baseline
python -m src.executor
python -m src.feedback.feedback_builder
python -m src.feedback.run_feedback
python -m src.feedback.execute_feedback
python -m src.metrics
```

## Baseline Workflow

The baseline workflow reads pilot operations from:

```text
datasets/pilot/pilot_operations.csv
```

It generates tests into:

```text
outputs/baseline/generated_tests.json
```

Then executes them into:

```text
outputs/baseline/execution_results.json
```

## Runtime Feedback Workflow

Runtime feedback uses baseline generated tests and baseline execution results.

Build feedback prompts:

```bash
python -m src.feedback.feedback_builder
```

Generate refined tests:

```bash
python -m src.feedback.run_feedback
```

Execute refined tests:

```bash
python -m src.feedback.execute_feedback
```

Feedback outputs:

```text
outputs/feedback/feedback_prompts.json
outputs/feedback/refined_tests.json
outputs/feedback/execution_results.json
```

## Metrics

Metrics are computed by:

```bash
python -m src.metrics
```

The metrics align with:

- RQ1 Endpoint Coverage: an operation is covered if at least one generated test exists for its `operation_uid`.
- RQ2 Fault Detection: a fault candidate is an execution result where `actual_status >= 500` or `actual_status` is not in the operation's documented response codes.

A fault candidate represents a potential inconsistency observed during runtime execution. It does not necessarily indicate a confirmed implementation defect. Authentication- or authorization-related responses (e.g., HTTP 401 or 403) may also be reported as fault candidates when those status codes are not documented in the corresponding OpenAPI specification.

Secondary runtime feedback metrics track status-match rates before and after feedback.

## Output Files

Primary outputs:

```text
outputs/baseline/generated_tests.json
outputs/baseline/execution_results.json
outputs/feedback/feedback_prompts.json
outputs/feedback/refined_tests.json
outputs/feedback/execution_results.json
outputs/results_summary.json
outputs/results_summary.csv
outputs/fault_candidates.csv
```

Additional analysis output:

```text
outputs/failure_analysis.csv
```

## Current Pilot Experiment Results (42 Operations)

- Total operations: 42
- Endpoint coverage: 100%
- Baseline status match rate: 0.00%
- Feedback status match rate: 33.33%
- Fault candidates: 42

These values come from the current pilot outputs and may change when datasets, prompts, models, or live API responses change.
