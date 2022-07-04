import os

CLIENT_ID = "{{ CLIENT_ID }}"  # Application (client) ID of app registration
AUTHORITY = "https://login.microsoftonline.com/{{ TENANT_ID }}"
REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.
ENDPOINT = (
    "https://graph.microsoft.com/v1.0/me"  # This resource requires no admin consent
)
SCOPES = ["User.ReadBasic.All"]
SESSION_TYPE = (
    "filesystem"  # Specifies the token cache should be stored in server-side session
)
KEYVAULT_URI = "https://{{ KEY_VAULT_NAME }}.vault.azure.net/"
SECRET_NAME = "{{ SECRET_NAME }}"
ROLES = ["Read"]