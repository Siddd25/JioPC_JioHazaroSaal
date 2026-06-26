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