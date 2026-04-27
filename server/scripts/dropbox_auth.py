"""One-time script to obtain a Dropbox refresh token.

Run once: python scripts/dropbox_auth.py
Then add the printed refresh token to your .env as DROPBOX_REFRESH_TOKEN.
"""

from dropbox import DropboxOAuth2FlowNoRedirect

app_key = input("App key: ").strip()
app_secret = input("App secret: ").strip()

auth_flow = DropboxOAuth2FlowNoRedirect(app_key, app_secret, token_access_type="offline")

print("\n1. Open this URL in your browser:")
print(auth_flow.start())
print("\n2. Click 'Allow', then paste the authorization code below.")
code = input("\nEnter auth code: ").strip()

result = auth_flow.finish(code)

print(f"\nRefresh token: {result.refresh_token}")
print("\nAdd these to your .env:")
print(f"  DROPBOX_APP_KEY={app_key}")
print(f"  DROPBOX_APP_SECRET={app_secret}")
print(f"  DROPBOX_REFRESH_TOKEN={result.refresh_token}")
