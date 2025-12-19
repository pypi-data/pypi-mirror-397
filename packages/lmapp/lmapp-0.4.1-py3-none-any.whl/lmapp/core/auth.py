import time
import requests
from typing import Optional, Dict, Any
from pathlib import Path
import json
import os
import keyring

class GitHubAuth:
    """
    Handles GitHub Device Flow Authentication.
    
    Reference: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow
    """
    
    # Standard GitHub Client ID for public apps (or we can use a specific one for lmapp)
    # For now, we might need the user to provide one or use a placeholder.
    # Ideally, lmapp should have its own registered OAuth App.
    # Using a placeholder for now.
    CLIENT_ID = "Ov23liVyx0Nr8DDvJvG5" 
    AUTH_URL = "https://github.com/login/device/code"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    SCOPE = "repo user" # Adjust scopes as needed
    SERVICE_NAME = "lmapp-github-auth"

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.access_token: Optional[str] = None

    def request_device_code(self) -> Dict[str, Any]:
        """
        Step 1: Request a device code from GitHub.
        Returns a dictionary containing device_code, user_code, verification_uri, etc.
        """
        headers = {"Accept": "application/json"}
        data = {
            "client_id": self.CLIENT_ID,
            "scope": self.SCOPE
        }
        
        try:
            response = requests.post(self.AUTH_URL, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to request device code: {e}")

    def poll_for_token(self, device_code: str, interval: int, expires_in: int) -> Optional[str]:
        """
        Step 2: Poll GitHub for the access token while the user authorizes the app.
        """
        headers = {"Accept": "application/json"}
        data = {
            "client_id": self.CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }

        start_time = time.time()
        
        while time.time() - start_time < expires_in:
            try:
                response = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=10)
                response.raise_for_status()
                result = response.json()

                if "access_token" in result:
                    self.access_token = result["access_token"]
                    self.save_token()
                    return self.access_token
                
                error = result.get("error")
                if error == "authorization_pending":
                    pass # User hasn't clicked yet
                elif error == "slow_down":
                    interval += 5 # GitHub asks us to slow down
                elif error == "expired_token":
                    raise TimeoutError("Device code expired")
                elif error == "access_denied":
                    raise PermissionError("User denied access")
                else:
                    raise RuntimeError(f"Authentication failed: {error}")

                time.sleep(interval)
                
            except requests.RequestException as e:
                # Network glitch, wait and retry
                time.sleep(interval)
                continue
                
        raise TimeoutError("Authentication timed out")

    def save_token(self):
        """Securely save the token using system keyring."""
        if not self.access_token:
            return
            
        try:
            keyring.set_password(self.SERVICE_NAME, "access_token", self.access_token)
        except Exception as e:
            # Fallback or log error (for now, we just print/log)
            print(f"Warning: Failed to save token to keyring: {e}")

    def load_token(self) -> Optional[str]:
        """Load the token from system keyring."""
        try:
            self.access_token = keyring.get_password(self.SERVICE_NAME, "access_token")
            return self.access_token
        except Exception:
            return None

    def is_authenticated(self) -> bool:
        """Check if we have a valid token."""
        return self.load_token() is not None
