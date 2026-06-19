# Part C - Desktop Presence Validation

## Overview

Part C validates the desktop presence and organization of applications against a YAML-defined expected state.

The validator performs the following checks for each application:

1. Verifies that the application's `.desktop` file exists in one of the standard Linux application locations:

   * `/usr/share/applications`
   * `~/.local/share/applications`

2. Verifies that the application shortcut is present in the expected desktop folder.

3. Verifies that the application's category matches the expected category.

Each application is classified as:

* **PASS** – Application is present and correctly configured.
* **MISPLACED** – Application exists but is located in the wrong folder or has an incorrect category.
* **MISSING** – Application `.desktop` file is not found on the system.

---

## Architecture

```text
YAML Test Cases
       ↓
Desktop Inventory Builder
       ↓
Desktop Folder Inventory Builder
       ↓
Validation Engine
       ↓
JSONL Log Generation
       ↓
Summary Report
```

---

## Directory Structure

```text
PartC/
├── validator.py
├── config/
│   └── tests.yaml
├── logs/
│   └── partc_log.jsonl
└── README.md
```

---

## Test Configuration

All test cases are defined in YAML.

Example:

```yaml
desktop_presence:
  - name: Coursera
    expected_folder: Education
    expected_category: Education

  - name: Chess
    expected_folder: Games
    expected_category: Game

  - name: PerplexityAI
    expected_folder: Productivity
    expected_category: Productivity
```

The validator is completely data-driven and does not contain application-specific logic.

---

## Validation Logic

### PASS

Application:

* Exists on the system.
* Exists in the expected desktop folder.
* Belongs to the expected category.

### MISSING

Application `.desktop` file is not found in:

* `/usr/share/applications`
* `~/.local/share/applications`

### MISPLACED

Application exists but:

* Is not present in the expected desktop folder, or
* Does not belong to the expected category.

---

## Logging

Results are written in JSON Lines format (`.jsonl`).

Each validation produces one log entry.

Example:

```json
{
  "timestamp": "2026-06-10T21:39:50.336708",
  "component": "C",
  "test_name": "Coursera",
  "result": "PASS",
  "duration_ms": 0.0034,
  "detail_message": "Everything in place"
}
```

Example failure:

```json
{
  "timestamp": "2026-06-10T21:39:50.336743",
  "component": "C",
  "test_name": "lovable",
  "result": "MISPLACED",
  "duration_ms": 0.0018,
  "detail_message": "Expected folder=productivity, App not found in expected desktop folder"
}
```

A summary record is appended at the end of the log:

```json
{
  "timestamp": "2026-06-10T21:39:50.336762",
  "component": "C",
  "type": "SUMMARY",
  "passed": 3,
  "misplaced": 3,
  "missing": 1
}
```

---

## Installation

Install required dependencies:

```bash
pip install pyxdg pyyaml
```

---

## Running

Execute:

```bash
python3 validator.py
```

The validator will:

1. Build an inventory of installed applications.
2. Build an inventory of desktop shortcuts.
3. Load test cases from YAML.
4. Perform validation.
5. Generate a JSONL log file.
6. Print a summary report.

---

## Design Decisions

### YAML for Test Cases

YAML is used because it is easy for humans to read and modify. Test cases can be added or updated without changing the validator code.

### JSONL for Logs

JSON Lines was chosen because it is:

* Machine readable
* Easy to parse
* Suitable for future LLM analysis
* Easy to process by automation tools

### Inventory-Based Validation

Application metadata is loaded once at startup into memory, avoiding repeated filesystem scans during validation and improving performance.

