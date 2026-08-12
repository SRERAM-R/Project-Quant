"""
Project Quant - Kite Access Token Generator.

One-off CLI script: prints the Kite login URL, exchanges the request token you paste back in for an access token, and prints it so
it can be copied into the other modules.

Author: Sreram R
"""

from kiteconnect import KiteConnect

api_key = ""
api_secret = ""

kite = KiteConnect(api_key=api_key)
print("\nPaste this url in the browser and copy the request token : ", kite.login_url())
request_token = input("\nPaste the request token here: ").strip()

try:
    data = kite.generate_session(request_token=request_token, api_secret=api_secret)
except Exception as error:
    raise SystemExit(f"Failed to generate session: {error}")

access_token = data["access_token"]
print("\nAccess token:", access_token)