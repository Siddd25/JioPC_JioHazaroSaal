# Installation

Detailed installation instructions, Debian package installation, virtual environment setup, dependency installation, and environment configuration are provided in **INSTALL.md**.

---

# Dependencies

The JioPC Automated Testing Agent is implemented in Python 3.12 and depends on the following packages:

| Dependency | Purpose |
|------------|---------|
| Playwright | Website and web application automation (Part A) |
| psutil | Process monitoring and resource usage collection |
| pyxdg | Parsing XDG Desktop Entry (`.desktop`) files |
| PyYAML | YAML configuration parsing |
| python-dotenv | Loading environment variables |
| OpenAI Python SDK | LLM-based log analysis |
| wmctrl | Native window detection for desktop applications |

System Requirements:

- Python 3.12+
- Chromium (installed through Playwright)
- Ubuntu 24.04 LTS (recommended)

---

# LLM Analysis Configuration

The optional log analysis module (`analyse.py`) uses any **OpenAI-compatible API**.

Before running analysis, configure the following environment variables:

```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o"
export LLM_API_KEY="<your-api-key>"
```

The analysis prompt is configured through the YAML file:

```yaml
analysis:
  prompt_file_path: ./prompts/analyse_log.txt
```

The prompt template can be modified without changing the source code, allowing different styles of executive summaries to be generated.

LLM analysis can be executed:

```bash
python jiopc_agent.py --config jiopc-agent.yaml --analyse
```

or independently on an existing log file:

```bash
python analyse.py \
    --log ~/.local/share/jiopc/agent/test_run_<timestamp>.log \
    --config jiopc-agent.yaml
```

---

# Log Format and Interpretation

The agent generates **newline-delimited JSON (JSONL)** logs.

Each line represents an independent execution event and can be parsed individually.

---

# Runtime Behavior

After installation, the agent performs only user-space, read-only operations. It does not require root privileges, install software, modify system files, or write outside the configured user log directory.

---

<br>

# Core Runner (`jiopc_agent.py`)

## Overview

`jiopc_agent.py` is the entry point of the JioPC Automated Testing Agent.

It is responsible for:

- Loading the YAML configuration.
- Building the desktop application inventory.
- Executing Parts A, B and C in the configured order.
- Monitoring the agent's own resource usage.
- Generating structured execution logs.
- Producing an overall execution summary.
- Optionally performing LLM-based log analysis.
- Optionally emailing the generated analysis report.

---

## Features

- Configuration-driven execution
- Modular execution of Parts A, B and C
- Execute individual components independently
- Configurable execution order
- Resource monitoring (Peak RAM and CPU usage)
- Structured JSON logging
- Automatic execution summary generation
- Optional LLM-based log analysis
- Optional email delivery of analysis reports

---

## Command Line Options

### Run Complete Test Suite

```bash
python jiopc_agent.py --config jiopc-agent.yaml
```

---

### Run Individual Components

```bash
python jiopc_agent.py --config jiopc-agent.yaml --part A

python jiopc_agent.py --config jiopc-agent.yaml --part B

python jiopc_agent.py --config jiopc-agent.yaml --part C
```

---

### Run Tests with LLM Analysis

```bash
python jiopc_agent.py \
    --config jiopc-agent.yaml \
    --analyse
```

---

### Run Tests with Email Delivery

```bash
python jiopc_agent.py \
    --config jiopc-agent.yaml \
    --analyse \
    --email recipient@example.com
```

---

## Execution Workflow

```text
Load YAML Configuration
          │
          ▼
Create Log File
          │
          ▼
Build Desktop Inventories
          │
          ▼
Start Resource Monitor
          │
          ▼
Execute Components
(A → B → C)
          │
          ▼
Generate Final Summary
          │
          ▼
Record Peak RAM & CPU Usage
          │
          ▼
(Optional)
LLM Log Analysis
          │
          ▼
(Optional)
Email Executive Summary
```

---

## Resource Monitoring

A background monitoring thread runs throughout the execution.

The following metrics are sampled periodically:

- Peak Resident Set Size (RSS) memory
- Peak CPU utilization

These metrics are written to the execution log after all tests complete.

Example:

```json
{
    "type": "RESOURCE_USAGE",
    "peak_agent_ram_mb": 58.7,
    "peak_agent_cpu_percent": 2.5
}
```

---

## Final Summary

After all enabled components finish execution, the runner generates a consolidated summary containing:

- Total execution time
- Total tests executed
- Component wise breakdown
- Total passed
- Total failed
- Total blocked
- Total degraded
- Total missing
- Total misplaced

Example:

```json
{
"type": "FINAL_SUMMARY", 
"timestamp": "2026-06-22T19:19:52.577014", 
"total_runtime_sec": 88.6, 
"component_A": 
        {
        "component": "A", 
        "type": "summary", 
        "TOTAL": 7, 
        "PASS": 5, 
        "FAIL": 1, 
        "BLOCKED": 1, 
        "SLOW": 0
        }, 

"component_B": 
        {
        "component": "B", 
        "type" : "summary",
        "TOTAL": 10, 
        "PASS": 10, 
        "FAIL": 0, 
        "DEGRADED": 0
        }, 
"component_C": 
        {
        "component": "C", 
        "type":"summary",
        "TOTAL": 15,
        "PASS": 7, 
        "MISPLACED": 8, 
        "MISSING": 0
         }, 
         
"total_tests": 32,
"total_pass": 22,
"total_fail": 1, 
"total_blocked": 1, 
"total_degraded": 0, 
"total_missing": 0, 
"total_misplaced": 8
}

```

---

## Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | All tests passed successfully |
| 1 | One or more tests failed, were blocked, degraded, missing or misplaced |

---

## Logging

Every execution generates newline-delimited JSON logs stored in:

```text
~/.local/share/jiopc/agent/
```

Generated files:

```
test_run_<timestamp>.log
test_run_<timestamp>.analysis.txt
```

---

## Design Decisions

- Execution order is configurable through the YAML file rather than being hard-coded.
- Each testing component (Part A, B and C) is implemented independently and orchestrated by the Core Runner.
- Resource monitoring executes concurrently in a background thread to minimize measurement overhead.
- Structured JSON logs are generated incrementally to simplify post-processing and LLM-based analysis.
- LLM analysis and email delivery are optional features that execute only when requested through command-line arguments.
- The runner returns standard process exit codes, making it suitable for integration into automated pipelines and CI/CD workflows.
---


<br>

# Part A – Website and Web Application Testing

Part A performs automated validation of websites and web applications using Playwright.

## Features

* Website accessibility verification
* HTTP error detection
* Page load time measurement
* UI element validation
* CAPTCHA and bot-protection detection
* Structured JSON logging

---

## Supported Validation Checks

| Type      | Description                                    |
| --------- | ---------------------------------------------- |
| role      | Verify presence of ARIA role                   |
| role_name | Verify ARIA role with specific accessible name |
| text      | Verify page text exists                        |
| selector  | Verify CSS selector exists                     |

---

## Example Configuration

```yaml
web_apps:
  - name: Chess.com
    url: https://www.chess.com
    timeout: 20
    load_threshold_ms: 2000
    bot_detection_expected: False

    checks:
      - type: role_name
        role: heading
        value: "Play Chess Online on the #1"
```

---

## Status Definitions

### PASS

Website loaded successfully and all configured checks passed.

### FAIL

Website returned an HTTP error or required UI elements were not found.

### BLOCKED

Bot protection, CAPTCHA, or anti-automation challenge detected.



Website which loaded successfully but exceeded the configured performance threshold is flagged as SLOW

---

## Sample Output

```json
{
"status": "PASS", "title": "Chess.com - Play Chess Online - Free Games", 
"load_time_ms": 1433, 
"expected_UI_elements_present": true, 
"load_threshold_ms": 2000, 
"threshold_exceeded": false, 
"detail": "Page loaded successfully and required UI elements verified", 
"website_name": "Chess.com", 
"url": "https://www.chess.com", 
"component": "A", 
"test_name": "Website and Web App Testing", 
"timestamp": "2026-06-25T20:41:36.807326"
}

```

---

## Technologies Used

* Python 3
* Playwright
* Chromium (Headless)
* YAML Configuration
* JSON Logging

---

## Generated Metrics

The component generates:

* Website status
* Page title
* Load time
* UI validation results
* HTTP validation results
* Bot detection results
* Execution summary

---

## Generated Summary

```json
{
"component": "A", 
"type": "summary", 
"TOTAL": 7, 
"PASS": 5, 
"FAIL": 1, 
"BLOCKED": 1, 
"SLOW": 1
}



```
---

<br>



# Part B – Native Application Launch and Health Validation

## Overview

Part B validates that native desktop applications installed on the system are correctly configured and operational.

For each application defined in the YAML configuration, the agent:

- Discovers the application from the desktop application inventory.
- Resolves the executable specified in the application's `.desktop` entry.
- Launches the application.
- Confirms that the process starts successfully.
- Verifies that a GUI window appears within the configured timeout.
- Ensures the application remains alive during the health observation period.
- Collects runtime resource metrics.
- Gracefully terminates the application and any spawned child processes.

Structured JSON logs are generated for every application together with an execution summary.

---

## Features

- Desktop application discovery
- Executable validation
- Native application launching
- GUI window verification
- Process health monitoring
- Runtime memory measurement
- Runtime CPU measurement
- Automatic cleanup of application process tree
- Structured JSON logging

---

## Validation Workflow

For every configured application the following validations are performed:

1. Verify application exists in desktop inventory.
2. Resolve executable from `.desktop` entry.
3. Launch application.
4. Verify process creation.
5. Verify GUI window creation.
6. Observe application stability.
7. Measure runtime metrics.
8. Close application and cleanup child processes.

---

## Status Definitions

### PASS

The application launched successfully, created a visible window, remained healthy throughout the observation period, and runtime metrics were collected.

### FAIL

Returned when any of the following occur:

- Application not found
- Executable cannot be resolved
- Process fails to launch
- Window does not appear before timeout

### DEGRADED

The application launches successfully but exits unexpectedly during the health observation period.

---

## Runtime Metrics

The following metrics are collected for every application:

- Launch time (ms)
- Resident Set Size (RSS) memory
- CPU utilization
- Executable location
- Expected desktop file
- Actual desktop file
- Process name
- Total execution time

---

## Window Detection

GUI validation uses:

- `wmctrl`
- `psutil`
- Recursive child-process discovery

The agent continuously monitors the launched process and its child processes. A GUI window is considered valid only when the owning PID belongs to the launched application's process tree, making the approach robust for applications that spawn separate GUI processes.

---

## Cleanup

After validation completes, the agent:

- Sends SIGTERM to the application's process group.
- Waits for graceful termination.
- Sends SIGKILL if required.
- Waits briefly before executing the next test.

This prevents orphaned processes and ensures test isolation.
---
## Example Configuration

```yaml
native_apps:

  - app_name : mpv Media Player
    process_name: mpvmediaplayer
    launch_timeout_s: 10
    desktop_file : /usr/share/applications/mpv.desktop
```

---

## Example Output

```json
{
"app_name": "LibreOffice Math", 
"actual_process_name": "oosplash", 
"window_detected": true, 
"launch_time_ms": 1072.24, 
"status": "PASS", 
"rss_mb": 6.79, 
"cpu_percent": 0.0,
"executable_location": "/usr/bin/libreoffice", "expected_desktop_file_location": "/usr/share/applications/libreoffice-math.desktop", 
"actual_desktop_file_location": "/usr/share/applications/libreoffice-math.desktop", 
"total_test_time_s": 9.164878606796265, 
"timestamp": "2026-06-25T20:43:07.700738", 
"test_name": "Native App Health Testing",
"component":"B"
}
```

## Generated Summary

```json
{
"component": "B", 
"type": "summary",
"TOTAL": 10, 
"PASS": 10, 
"FAIL": 0, 
"DEGRADED": 0
}


```

## Technologies Used

- Python 3
- psutil
- wmctrl
- XDG Desktop Entry
- subprocess
- Linux process groups

---


# Part C – Desktop Presence and Classification Validation

## Overview

Part C verifies that desktop applications are correctly registered within the Linux desktop environment.

For each application defined in the YAML configuration, the agent validates:

- Presence of the application's `.desktop` entry.
- Correct desktop category assignment.
- Presence of the desktop shortcut in the expected desktop folder.

Unlike Part B, this component does **not** launch applications. It performs static validation using the desktop application inventory generated from installed XDG Desktop Entry files.

Structured JSON logs are generated for every application together with a summary report.

---

## Features

- Desktop application discovery
- Desktop category validation
- Desktop shortcut folder validation
- Missing application detection
- Misclassification detection
- Structured JSON logging

---

## Validation Workflow

For every configured application the following validations are performed:

1. Verify the application's `.desktop` entry exists.
2. Verify the application belongs to the expected XDG category.
3. Verify the application shortcut exists in the expected desktop folder.
4. Record validation result.

---

## Status Definitions

### PASS

The application:

- Exists on the system.
- Belongs to the expected desktop category.
- Appears in the expected desktop shortcut folder.

### MISPLACED

The application exists but one or more placement validations fail.

Examples:

- Incorrect desktop category.
- Missing from the expected desktop shortcut folder.

### MISSING

No matching `.desktop` entry was found for the application.

---

## Validation Sources

The agent validates applications using:

- Installed `.desktop` files
- XDG Desktop Entry metadata
- Desktop folder inventory
- YAML configuration
---
## Example Configuration

```yaml
desktop_presence:
  - name: duolingo
    expected_category: Education
    expected_desktop_folder: Education
```

---

## Example Output

```json
{
"timestamp": "2026-06-22T20:01:17.786616", 
"component": "C", 
"test_name" : "App presence Testing",
"app_name": "qpdfview", 
"result": "MISPLACED", 
"duration_ms": 0.0022, 
"detail_message": 
"Expected folder=productivity, App not found in expected desktop folder"
}

```

## Generated Summary

```json
{
"component": "C", 
"type": "summary",
"TOTAL": 15,  
"PASS": 7, 
"MISPLACED": 8, 
"MISSING": 0
}


```

---

## Technologies Used

- Python 3
- pyxdg
- XDG Desktop Entry
- JSON Logging


---

# LLM-Based Log Analysis

The agent provides an optional post-execution analysis module that summarizes the generated test logs using a Large Language Model (LLM).

The analyzer converts the structured JSON execution log into a concise executive summary highlighting system health, failures, and recommendations.

---

## Features

- Reads structured JSON logs generated by the test agent.
- Uses a configurable prompt template.
- Supports any OpenAI-compatible API endpoint.
- Generates a human-readable executive summary.
- Saves the analysis as a text report.
- Optionally emails the report to a specified recipient.

---

## Execution Flow

```text
JSON Log
    │
    ▼
Load Prompt Template
    │
    ▼
Build LLM Prompt
    │
    ▼
OpenAI-Compatible API
    │
    ▼
Executive Summary
    │
    ├── Print to Console
    ├── Save as .analysis.txt
    └── (Optional) Email Report
```

---

## Environment Variables

The analyzer requires the following environment variables:

```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o"
export LLM_API_KEY="<your-api-key>"
```

Any OpenAI-compatible endpoint can be used (e.g., OpenAI, Groq, Together AI, OpenRouter, local vLLM, Ollama with an OpenAI-compatible API, etc.).

---

## YAML Configuration

The analyzer is configured through the `analysis` section of the YAML file.

Example:

```yaml
analysis:
  prompt_file_path: ./prompts/analyse_log.txt
```

| Field | Description |
|--------|-------------|
| prompt_file_path | Path to the prompt template used for log analysis |

---

## Running Analysis

Analyse an existing log file:

```bash
python analyse.py \
    --log ~/.local/share/jiopc/agent/test_run_<timestamp>.log \
    --config jiopc-agent.yaml
```

Run the entire test suite followed by analysis:

```bash
python jiopc_agent.py \
    --config jiopc-agent.yaml \
    --analyse
```

Generate the report and email it to a recipient:

```bash
python jiopc_agent.py \
    --config jiopc-agent.yaml \
    --analyse \
    --email recipient@example.com
```

---

## Prompt Template

The analyzer separates prompt engineering from implementation.

The prompt template is stored as a plain text file and is loaded at runtime, making it easy to customize the analysis without modifying the source code.


---

## Generated Output

The analyzer produces a human-readable report.



The report is automatically saved alongside the log file as:

```
test_run_<timestamp>.analysis.txt
```

---

## Email Delivery (Optional)

When the `--email` argument is supplied, the generated executive summary is sent to the specified recipient via SMTP.

SMTP credentials are provided through environment variables:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="<gmail-app-password>"
```

---

## Design Decisions

- Uses an OpenAI-compatible client, allowing different LLM providers to be used without changing the implementation.
- Prompt templates are stored externally, enabling easy customization of the analysis behavior.
- Environment variables are used for API credentials and SMTP configuration to avoid storing secrets in the repository.
- Analysis is optional and can be executed **independently** on previously generated log files.

---

Additional design details about implementation of the three components (A,B,C) and detailed config file YAML schema is available in **DESIGN.md**
