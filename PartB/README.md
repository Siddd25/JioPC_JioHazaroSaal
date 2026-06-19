# Part B - Native Application Health Validation

## Overview

Part B validates that native desktop applications can be launched successfully and reach a healthy running state.

For each application defined in the YAML configuration, the validator:

1. Locates the application's `.desktop` file.
2. Extracts and validates the executable from the `Exec=` field.
3. Launches the application.
4. Verifies that a process appears within a configurable timeout.
5. Monitors the process for 5 seconds.
6. Verifies that the actual process name matches the expected process name.
7. Collects memory (RSS) and CPU usage metrics.
8. Terminates the application cleanly.
9. Writes results to a JSON Lines (`.jsonl`) log.

---

## Architecture

```text
YAML Test Cases
       ↓
Desktop Inventory Builder
       ↓
Exec Extraction
       ↓
Executable Validation
       ↓
Application Launch
       ↓
Process Detection
       ↓
Health Monitoring
       ↓
Resource Collection
       ↓
Graceful Termination
       ↓
JSONL Logging
```

---

## Project Structure

```text
PartB/
├── validator.py
├── config/
│   └── test.yaml
├── logs/
│   └── partb_log.jsonl
└── README.md
```

---

## Test Configuration

Applications are defined in YAML.

Example:

```yaml
PartB:
  - app_name: Audacious
    process_name: audacious
    timeout: 10

  - app_name: FeatherNotes
    process_name: feathernotes
    timeout: 10
```

### Fields

| Field        | Description                                       |
| ------------ | ------------------------------------------------- |
| app_name     | Application name used to locate the desktop entry |
| process_name | Expected process name after launch                |
| timeout      | Maximum time allowed for process appearance       |

---

## Validation Logic

### PASS

Application:

* Desktop entry exists.
* Executable exists.
* Process appears within timeout.
* Process survives health observation window.
* Process name matches expected value.
* Resource metrics successfully collected.

### FAIL

Application:

* Desktop entry not found, or
* Executable not found, or
* Process fails to appear within timeout, or
* Process name does not match expected value.

### DEGRADED

Application:

* Process appears initially.
* Process terminates unexpectedly before health validation completes.

---

## Health Validation

After launch:

1. The validator waits for the process to appear.
2. The process is monitored for 5 seconds.
3. If the process exits during this period, the result is classified as `DEGRADED`.
4. If the process remains alive, memory and CPU metrics are collected.

---

## Resource Metrics

### Memory

Resident Set Size (RSS) is collected using:

```python
process.memory_info().rss
```

and reported in megabytes.

### CPU

CPU usage is collected using:

```python
process.cpu_percent()
```

and reported as a percentage.

---

## Process Verification

The validator confirms that the actual process name matches the expected process name supplied in the YAML configuration.

Example:

```yaml
process_name: audacious
```

Expected runtime process:

```text
audacious
```

---

## Logging

Results are written in JSON Lines format (`.jsonl`).

Each application produces one log entry.

Example:

```json
{
  "actual_process_name": "audacious",
  "app_name": "Audacious",
  "status": "PASS",
  "rss_mb": 48.18,
  "cpu_percent": 1.0,
  "executable_location": "/usr/bin/audacious",
  "desktop_file": "/usr/share/applications/audacious.desktop",
  "total_time": 6.09,
  "timestamp": "2026-06-13T21:54:33.158533",
  "component": "B"
}
```

Summary record:

```json
{
  "part": "B",
  "PASS": 2,
  "FAIL": 1,
  "DEGRADED": 0
}
```

---

## Exec Field Handling

Desktop entry `Exec=` fields may contain placeholder tokens such as:

```text
%f
%F
%u
%U
```

These tokens are removed before launch because the validator performs application health validation rather than file or URL opening.

Example:

```text
firefox %u
```

becomes:

```text
firefox
```

before execution.

---

## Installation

Install required dependencies:

```bash
pip install pyxdg pyyaml psutil
```

---

## Running

Execute:

```bash
python3 validator.py
```

The validator will:

1. Build an inventory of installed desktop applications.
2. Load YAML test definitions.
3. Launch and validate applications.
4. Collect health metrics.
5. Generate JSONL logs.
6. Print execution results.

---

## Design Decisions

### YAML for Test Definitions

YAML was chosen because it is easy to read and modify by humans while remaining machine-parsable.

### JSONL for Logs

JSON Lines was chosen because it:

* Is machine-readable.
* Supports one result per line.
* Is easy to process by automation tools.
* Is suitable for future LLM-based analysis.

### Inventory-Based Discovery

Application metadata is collected once at startup and cached in memory, avoiding repeated filesystem scans during validation.

### Lightweight Execution Model

Applications are launched one at a time and terminated immediately after health validation. This minimizes resource consumption and reduces interference with normal desktop operation.

