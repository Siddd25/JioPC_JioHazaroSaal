# Part A – Website and Web Application Testing Design

## Objective

Part A validates websites and web applications to ensure that:

* The website is reachable.
* Expected UI elements are present.
* Page load performance is within acceptable limits.
* HTTP errors are detected.
* Bot protection or CAPTCHA mechanisms are identified.

---

## Architecture

```text
YAML Configuration
        │
        ▼
 PartATester.run()
        │
        ▼
 Playwright Chromium
        │
        ▼
 Website Navigation
        │
 ┌──────┼───────────┐
 ▼      ▼           ▼
HTTP   UI Check   Bot Check
Check Verification Detection
 └──────┼───────────┘
        ▼
 Structured JSON Logs
```

---

## Execution Flow

### 1. Configuration Loading

Each website entry is loaded from YAML configuration.

Example:

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

The following parameters are used:

* URL
* Timeout
* UI validation checks
* Load threshold
* Bot detection expectation

---

### 2. Browser Launch

A Playwright Chromium browser is launched in headless mode.

```python
browser = p.chromium.launch(headless=True)
```

---

### 3. Website Navigation

The agent navigates to the target website using:

```python
page.goto(
    url,
    wait_until="domcontentloaded"
)
```

Page load time is measured from navigation start until DOM content is available.

---

### 4. Bot Protection Detection

The component detects common anti-automation mechanisms.

#### Supported Detection Methods

##### CAPTCHA Detection

Checks for:

* Google reCAPTCHA
* hCaptcha
* Cloudflare Turnstile
* CAPTCHA iframes
* Known challenge widgets

##### Keyword Detection

Checks page title and body for:

* Verify you are human
* CAPTCHA
* Security Check
* Checking your browser
* Access Denied
* Unusual traffic
* Robot check

Detected bot protection is reported as:

```json
{
  "status": "BLOCKED"
}
```

---

### 5. HTTP Validation

HTTP response codes are validated.

Responses with status codes:

```text
>= 400
```

are marked as:

```json
{
  "status": "FAIL"
}
```

---

### 6. UI Validation

Configured UI checks are executed after page load.

Supported validation types:

#### Role Validation

```yaml
type: role
value: button
```

#### Role + Accessible Name Validation

```yaml
type: role_name
role: button
value: Login
```

#### Text Validation

```yaml
type: text
value: Sign In
```

#### CSS Selector Validation

```yaml
type: selector
value: "#login-btn"
```

---

### 7. Performance Validation

Page load time is compared against the configured threshold.

If:

```text
load_time_ms > load_threshold_ms
```

the website is marked as:

```json
{
  "threshold_exceeded": true
}
```

and counted in the SLOW category.

---

## Output Metrics

For each website:

* Status
* Website title
* Load time (ms)
* UI verification result
* Threshold status
* Bot protection status

Summary metrics:

* TOTAL
* PASS
* FAIL
* BLOCKED
* SLOW

---

## Assumptions

* Internet connectivity is available.
* Chromium is installed through Playwright.
* Websites are publicly accessible.
* UI checks accurately represent expected website behaviour.

---

## Limitations

* Authentication flows are not validated.
* Complex user interactions are not simulated.
* Dynamic anti-bot systems may evolve beyond supported signatures.
* Performance metrics depend on network and VM conditions at runtime.
* Captcha detection includes keyword matching.

---


# Part B – Native Application Testing Design

## Objective

Part B verifies that desktop applications installed on the Linux system can be successfully launched, create a graphical window, remain operational during a health observation period, and expose basic runtime metrics.

---

# Architecture

```text
YAML Configuration
        │
        ▼
Desktop Application Inventory
        │
        ▼
Locate .desktop Entry
        │
        ▼
Resolve Executable
        │
        ▼
Launch Application
        │
        ▼
┌────────────────────────────────────┐
│ Process Detection                  │
│ Window Detection (wmctrl)          │
│ Child Process Discovery            │
└────────────────────────────────────┘
        │
        ▼
Health Observation
        │
        ▼
Resource Metrics Collection
        │
        ▼
Process Cleanup
        │
        ▼
Structured JSON Logging
```

---

## Execution Flow

### Step 1 – Application Discovery

Applications are searched within the desktop inventory built from installed `.desktop` files.

The inventory provides:

- Desktop entry
- Executable command
- Categories
- Desktop file location

---

### Step 2 – Executable Resolution

The executable command is extracted from the `Exec` field of the desktop entry.

Desktop entry placeholders such as:

- `%f`
- `%F`
- `%u`
- `%U`

are removed before execution.

The executable path is then validated using `shutil.which()`.

Failure to resolve the executable immediately marks the application as **FAIL**.

---

### Step 3 – Application Launch

Applications are launched using Python's `subprocess.Popen()`.

Each application starts in a separate process group to simplify cleanup and ensure that child processes can be terminated safely.

---

### Step 4 – Process Validation

The agent confirms that the launched process appears before the configured timeout expires.

Failure to create a process results in a **FAIL** status.

---

### Step 5 – GUI Window Validation

The desktop environment is continuously monitored using `wmctrl`.

The agent also discovers all recursively spawned child processes using `psutil`.

A GUI window is considered valid only when the owning PID belongs to the launched application's process tree.

This approach supports applications such as LibreOffice or Flatpak applications that create separate GUI processes.

---

### Step 6 – Health Observation

After successful startup, the application is monitored for a fixed observation period.

If the application exits unexpectedly during this interval, the result is classified as **DEGRADED** instead of **FAIL**, indicating that launch succeeded but runtime stability was insufficient.

---

### Step 7 – Runtime Metrics

Once the application remains healthy, the following metrics are collected:

- Launch latency
- Resident Set Size (RSS)
- CPU utilization
- Process name

These provide lightweight runtime health information without intrusive profiling.

---

### Step 8 – Cleanup

After testing completes:

1. SIGTERM is sent to the application process group.
2. A grace period is provided for clean shutdown.
3. SIGKILL is issued if any processes remain.
4. Applies a **2-second cooldown** before starting the next application test.

This guarantees clean isolation between application tests.

---

## Design Decisions

- `.desktop` files are treated as the authoritative source for application discovery.
- GUI validation is based on process ownership rather than window title matching to improve reliability.
- Recursive child-process discovery supports modern multi-process desktop applications.
- Process groups simplify cleanup and eliminate orphaned processes.
- Structured JSON logs enable automated post-processing and LLM-based analysis.

---

## Assumptions

- Applications expose valid XDG desktop entries.
- `wmctrl` is installed.
- A graphical desktop session is available.
- Applications can be launched from their desktop entries.

---

## Limitations

- Console-only applications are outside the scope of this component.
- Functional application behaviour beyond launch verification is not tested.
- Runtime metrics are collected over a short observation period and do not represent long-duration stress testing.


---
# Part C – Start Menu & Desktop App Presence 

## Objective

Part C validates that desktop applications are correctly registered within the Linux desktop environment according to the expected desktop organization specified in the YAML configuration.

The component verifies application presence, desktop categorization, and desktop shortcut placement without launching the application.

---

# Architecture

```text
YAML Configuration
        │
        ▼
Desktop Application Inventory
        │
        ▼
Locate .desktop Entry
        │
        ▼
Category Validation
        │
        ▼
Desktop Folder Validation
        │
        ▼
Classification Result
        │
        ▼
Structured JSON Logging
```

---

## Execution Flow

### Step 1 – Application Discovery

Applications are searched within the desktop inventory built from installed `.desktop` files.

Each inventory entry contains:

- Application name
- Categories
- Desktop file location
- Executable information

---

### Step 2 – Presence Validation

The component verifies that a matching desktop entry exists.

If no matching application is found, the result is immediately classified as:

```
MISSING
```

---

### Step 3 – Category Validation

The application's XDG categories are extracted from its `.desktop` file.

The expected category specified in the YAML configuration is compared against the application's registered categories.

If the expected category is absent, the result is classified as:

```
MISPLACED
```

---

### Step 4 – Desktop Folder Validation

The desktop folder inventory is consulted to verify that the application's desktop shortcut exists in the expected folder.

Failure to locate the application within the configured desktop folder results in:

```
MISPLACED
```

---

### Step 5 – Result Classification

Applications are classified as:

| Result | Meaning |
|---------|---------|
| PASS | Present, correctly categorized, and correctly placed |
| MISPLACED | Present but incorrectly categorized or placed |
| MISSING | Desktop entry not found |

---

### Step 6 – Structured Logging

Each validation generates a structured JSON record containing:

- Timestamp
- Component identifier
- Application name
- Validation result
- Execution duration
- Detailed diagnostic message

After all applications are processed, a summary containing total PASS, MISPLACED, and MISSING counts is generated.

---

## Design Decisions

- Desktop validation is performed without launching applications, reducing execution time and resource usage.
- Installed `.desktop` files serve as the authoritative source for application metadata.
- Category validation uses XDG Desktop Entry categories rather than folder names.
- Desktop folder validation ensures applications are organized according to the expected desktop layout defined in the YAML configuration.
- Structured JSON logs enable automated reporting and downstream LLM-based analysis.

---

## Assumptions

- Applications expose valid XDG Desktop Entry files.
- Desktop inventories have been successfully generated before validation.
- Desktop folder names defined in the YAML configuration correspond to the generated desktop folder inventory.

---

## Limitations

- Validation is limited to applications represented by `.desktop` entries.
- Functional application behavior is not tested.
- Desktop appearance, icons, and visual themes are outside the scope of this component.
- Folder validation depends on the accuracy of the generated desktop folder inventory.

---
# YAML Configuration Schema

The agent is completely configuration-driven. All tests are defined in a single YAML configuration file.

---

## Top-Level Structure

```yaml
test_agent:
  ...

analysis:
  ...
  
web_apps:
  ...

native_apps:
  ...

desktop_presence:
  ...

email:
  ...
```

---

## test_agent

Global execution settings.

```yaml
test_agent:
  execution_order:
    - A
    - B
    - C

  log_dir: ~/.local/share/jiopc/agent
```

| Field | Description |
|--------|-------------|
| execution_order | Order in which components execute |
| log_dir | Directory where JSON logs are stored |

---

## web_apps (Part A)

Defines websites to validate.

```yaml
web_apps:

- name: Chess.com
  url: https://www.chess.com
  timeout: 15
  load_threshold_ms: 2000
  bot_detection_expected: True

  checks:
    - type: role_name
      role: heading
      value: "Play chess"
```

| Field | Description |
|--------|-------------|
| name | Friendly website name |
| url | Website URL |
| timeout| Maximum navigation timeout |
| load_threshold_ms | Performance threshold |
| bot_detection_expected| Boolean value for whether bot detection is possible on the url|
| checks| UI elements expected after page load |


Supported UI validation checks:

- text
- selector
- role
- role_name

---

## native_apps (Part B)

Defines applications to launch.

```yaml
native_apps:

- app_name: Calculator
  desktop_file: /usr/share/applications/org.gnome.Calculator.desktop
  launch_timeout_s: 10
```

| Field | Description |
|--------|-------------|
| app_name | Application name |
| desktop_file | Expected desktop entry location |
| launch_timeout_s | Maximum time allowed for application launch |

---

## desktop_presence (Part C)

Defines desktop validation rules.

```yaml
desktop_presence:

- name: Calculator
  expected_category: Utility
  expected_desktop_folder: Utilities
```

| Field | Description |
|--------|-------------|
| name | Application name |
| expected_category | Expected XDG category |
| expected_desktop_folder | Expected desktop shortcut folder |

---

## email

Optional email configuration.

```yaml
email:
  sender: jiopc331@gmail.com
```

SMTP credentials are **not stored** inside the YAML file.

They are supplied using environment variables:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="example@gmail.com"
export SMTP_PASSWORD="<app-password>"
```