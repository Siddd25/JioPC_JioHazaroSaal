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