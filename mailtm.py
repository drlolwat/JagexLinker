from DrissionPage import ChromiumPage, ChromiumOptions
import argparse
import time
import requests
import re

parser = argparse.ArgumentParser(description='Run browser automation with Mail.tm inbox.')
parser.add_argument('--port', type=int, default=9222, help='Local port number for the browser connection.')
parser.add_argument('--email', type=str, required=True, help='Login email.')
parser.add_argument('--password', type=str, required=True, help='Login password.')
parser.add_argument('--mail_password', type=str, required=True, help='Mail.tm password.')

args = parser.parse_args()

def extract_code(subject):
    match = re.search(r'\b([A-Z0-9]{5})\b', subject)
    return match.group(1) if match else None

def get_mailtm_token(email, password):
    r = requests.post("https://api.mail.tm/token", json={"address": email, "password": password})
    return r.json()["token"] if r.ok else None

def wait_for_code(token):
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(60):
        r = requests.get("https://api.mail.tm/messages", headers=headers)
        if r.ok and r.json()["hydra:member"]:
            for msg in r.json()["hydra:member"]:
                if "verification code" in msg["subject"].lower():
                    return extract_code(msg["subject"])
        time.sleep(2)
    return None

js_code = """
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
let screenX = getRandomInt(800, 1200);
let screenY = getRandomInt(400, 600);
Object.defineProperty(MouseEvent.prototype, 'screenX', { value: screenX });
Object.defineProperty(MouseEvent.prototype, 'screenY', { value: screenY });
"""

try:
    co = ChromiumOptions().set_local_port(args.port)
    page = ChromiumPage(addr_or_opts=co)

    time.sleep(4)
    challengeSolution = page.ele("@name=cf-turnstile-response")
    if challengeSolution:
        wrapper = challengeSolution.parent()
        iframe = wrapper.shadow_root.ele("tag:iframe")
        iframe.run_js(js_code)
        button = iframe.ele("tag:body").shadow_root.ele("tag:input")
        button.click()

    email_field = page.ele('#email')
    if email_field:
        print("Entering email...")
        email_field.input(args.email)
        cont = page.ele('#continue-with-assisted-via-email-flow')
        if cont:
            cont.click()

        password_field = page.ele('#password', timeout=10)
        if password_field:
            print("Entering password...")
            password_field.input(args.password)
            login_button = page.ele('#assisted-login--credentials-form--continue-button')
            if login_button:
                login_button.click()

        mfa_continue = page.ele('@data-testid=continue-with-totp-mfa', timeout=10)
        if mfa_continue:
            mfa_continue.click()

        print("Waiting for Mail.tm code...")
        token = get_mailtm_token(args.email, args.mail_password)
        code = wait_for_code(token)

        if code:
            print(f"Got code: {code}")
            input_field = page.ele('#totp-verify-form--input-code')
            if input_field:
                input_field.input(code)
                submit = page.ele('#totp-verify-form--button-continue')
                if submit:
                    submit.click()
        else:
            print("Failed to get verification code.")
    else:
        print("Email field not found.")

except Exception as e:
    print(f"Exception: {e}")