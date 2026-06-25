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
