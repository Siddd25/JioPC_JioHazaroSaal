from playwright.sync_api import sync_playwright
import yaml
import time
import json
from datetime import datetime

PASS  =0
FAIL =0
BLOCKED =0
SLOW = 0

def detect_bot_block(page):
    title = page.title().lower()

    body_text = page.locator("body").inner_text().lower()


    challenge_selectors = [
        "iframe[src*='captcha']",
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "iframe[src*='turnstile']",
        "iframe[src*='challenges.cloudflare']",
        "[data-sitekey]"
    ]

    for selector in challenge_selectors:

        try:
            if page.locator(selector).count() > 0:
                return True

        except Exception:
            pass
    
    blocked_keywords = [
        "captcha",
        "verify you are human",
        "are you human",
        "are you a robot",
        "robot check",
        "checking your browser",
        "just a moment",
        "security check",
        "unusual traffic",
        "access denied",
        "attention required"
    ]

    if any(
        keyword in title or keyword in body_text
        for keyword in blocked_keywords
    ):
        return True

 
    return False



def verify_checks(page, checks):

    for check in checks:

        check_type = check["type"]
        value = check["value"]

        if check_type == "role":

            page.get_by_role(
                value
            ).first.wait_for(
                timeout=5000
            )
        elif check_type == "role_name":
            page.get_by_role(check["role"], name = check["value"]).wait_for(
                timeout=5000
            )

        elif check_type == "text":

            page.get_by_text(
                value
            ).wait_for(
                timeout=5000
            )

        elif check_type == "selector":

            page.wait_for_selector(
                value,
                timeout=5000
            )

        else:

            raise Exception(
                f"Unknown check type: {check_type}"
            )


def test_website(url, checks, timeout,load_threshold_ms):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()
        

        try:

            start = time.time()

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=timeout * 1000
            )
            
            if response and response.status >= 400:
                return {
        "status": "FAIL",
        "detail": f"HTTP {response.status}"
        }
            

            load_time_ms = round(
                (time.time() - start) * 1000
            )
            threshold_exceeded = (load_time_ms > load_threshold_ms)

            if detect_bot_block(page):

                return {
                    "status": "BLOCKED",
                    "detail": "Bot protection or CAPTCHA detected"
                }
                

            verify_checks(
                page,
                checks
            )

            return {
                "status": "PASS",
                "title" : page.title(),
                "load_time_ms": load_time_ms,
                "expected_UI_elements_present" : True,
                "load_threshold_ms" : load_threshold_ms,
                "threshold_exceeded" : threshold_exceeded

            }
            
            

        except Exception as e:

            return {
                "status": "FAIL",
                "detail": str(e)
            }
            

        finally:

            browser.close()





with open("config/test.yaml") as f:
    data = yaml.safe_load(f)


log_file = open("partA.jsonl", "w")

for site in data["PartA"]:

    result = test_website(
        site["url"],
        site["checks"],
        site["timeout"],
        site["load_threshold_ms"]
    )
    if result.get("threshold_exceeded"):
        SLOW+=1
    if result['status'] == "PASS":
        PASS+=1
    if result['status'] == "FAIL":
        FAIL+=1
    if result['status'] == "BLOCKED":
        BLOCKED +=1


    result['website_name'] = site['name']
    result['url'] = site ['url']
    result['COMPONENT'] = "A"
    result['test_name'] = "Website and Web App Testing"
    result['timestamp'] = datetime.now().isoformat()


    log_file.write(json.dumps(result) + "\n")

summary = {'COMPONENT': "A", "type": 'summary', 'TOTAL': len(data['PartA']), "PASS": PASS, "FAIL": FAIL, "BLOCKED" : BLOCKED, "SLOW" :SLOW}  
    
log_file.write(json.dumps(summary) + "\n")

log_file.close()
