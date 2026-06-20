from playwright.sync_api import sync_playwright
import yaml
import time


def detect_bot_block(page):

    text = page.locator("body").inner_text().lower()

    blocked_keywords = [
        "captcha",
        "verify you are human",
        "are you human",
        "are you a robot",
        "robot check",
        "checking your browser",
        "just a moment",
        "cloudflare",
        "security check",
        "unusual traffic",
        "access denied"
    ]

    return any(
        keyword in text
        for keyword in blocked_keywords
    )


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


def test_website(url, checks, timeout):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()
        page.goto(url)
        page.pause()
        

        






test_website("https://www.khanacademy.org",[],100000)