from DrissionPage import ChromiumPage, ChromiumOptions
import argparse
import pyotp


# Set up argument parsing
parser = argparse.ArgumentParser(description='Run browser automation with custom settings.')
parser.add_argument('--port', type=int, default=9222, help='Local port number for the browser connection.')
parser.add_argument('--email', type=str, required=True, help='Login email.')
parser.add_argument('--password', type=str, required=True, help='Login password.')
parser.add_argument('--totp_secret', type=str, required=True, help='TOTP secret key for generating OTP codes.')

args = parser.parse_args()

# Generate the current OTP code
totp = pyotp.TOTP(args.totp_secret)
current_otp = totp.now()

try:
    co = ChromiumOptions().set_local_port(args.port)  # Use the port number from arguments
    page = ChromiumPage(addr_or_opts=co)
    print(page.title)
    
    
    blocked_message_element = page.ele('@id=cloudflare_title').text

    if 'Sorry, you have been blocked' in blocked_message_element:
        print("Proxy has been blocked. Exiting the program.")
    else:
        print("No proxy block detected. Continuing the program.")
        print("LolwatbigPP DebugPrint")
        # Handle Kekflare checkbox
        iframe = page.get_frame('@src^https://challenges.cloudflare.com/cdn-cgi')
        element = iframe('.mark')
        print("CF CLICK!")
        element.click()
        
        # Check if the email field exists
        email_field = page.ele('#email')  # Adjust the selector if necessary
        if email_field:
            print("Email field found. Entering email...")
            email_field.input(args.email)
            # Click on the continue button after entering the email
            continue_button = page.ele('#continue-with-assisted-via-email-flow')
            if continue_button:
                print("Continue button found. Clicking...")
                continue_button.click()
            else:
                print("Continue button not found.")
                
            # Wait for password field and enter the password
            password_field = page.ele('#password', timeout=10)  # Adjust timeout as needed
            if password_field:
                print("Password field found. Entering password...")
                password_field.input(args.password)
                # Click on the login button after entering the password
                login_button = page.ele('#assisted-login--credentials-form--continue-button')
                if login_button:
                    print("Login button found. Clicking...")
                    login_button.click()
                else:
                    print("Login button not found.")
            else:
                print("Password field not found.")
            
            # Click on the continue with TOTP MFA button
            mfa_continue_button = page.ele('@data-testid=continue-with-totp-mfa', timeout=10)
            if mfa_continue_button:
                print("MFA Continue button found. Clicking...")
                mfa_continue_button.click()
            else:
                print("MFA Continue button not found.")
            
            # Wait for TOTP input field and enter the OTP code
            totp_field = page.ele('#totp-verify-form--input-code', timeout=10)
            if totp_field:
                print("TOTP field found. Entering OTP code...")
                totp_field.input(current_otp)  # Enter the dynamically generated OTP code
                # Click on the continue button after entering the OTP code
                totp_continue_button = page.ele('#totp-verify-form--button-continue')
                if totp_continue_button:
                    print("TOTP Continue button found. Clicking...")
                    totp_continue_button.click()
                else:
                    print("TOTP Continue button not found.")
            else:
                print("TOTP field not found.")
        else:
            print("Email field not found.")

except Exception as e:
    print(f"Failed to connect to the browser: {e}")