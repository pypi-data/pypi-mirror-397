#!/usr/bin/env python3
"""
Auth Service for QINA Security Editor
Handles login, API key verification, and config updates.
"""

import json
import os
import requests
from typing import Optional, Dict, Any
from .config_manager import ConfigManager

# Environment-based URLs
def get_api_base_url():
    """Get the API base URL (QA or Production)"""
    return os.environ.get('CLOUDDEFENSE_API_BASE_URL', 'https://console.clouddefenseai.com')


def _debug(msg: str):
    if os.environ.get("QINA_DEBUG_AUTH"):
        print(f"[AUTH DEBUG] {msg}")

LOGIN_URL = f"{get_api_base_url()}/cd-auth/login"
VERIFY_URL = f"{get_api_base_url()}/api/ide/auth/verify"


class AuthService:
    def __init__(self, config: ConfigManager):
        self.config = config
        self._session_token: Optional[str] = None

    def ensure_credentials(self, prompt_fn=input, secret_prompt_fn=input) -> Dict[str, Any]:
        """Ensure api_key and team_id exist in config, prompting user if needed.
        Returns dict with api_key and team_id.
        """
        # 0) Use saved config if available
        api_key = self.config.get_api_key()
        team_id = self.config.get_team_id()
        if api_key and team_id:
            return {"api_key": api_key, "team_id": team_id}

        # 1) Ask for API key first (best UX for terminal tools)
        print("\nEnter your QINA API key (or press Enter to login and fetch it):")
        print("  Get it from: https://console.clouddefenseai.com/integrations/qina")
        api_key = prompt_fn("QINA API key: ").strip()

        token: Optional[str] = None

        if api_key:
            # Try verifying without login
            team_id = self._verify_api_key(None, api_key)
            if team_id:
                self.config.set_api_key(api_key)
                self.config.set_team_id(team_id)
                return {"api_key": api_key, "team_id": team_id}
            # If verification fails, fall back to login to obtain token and retry
            print("\nAPI key verification requires login. Please enter your CloudDefense credentials.")

        # 2) Login to get token (only if needed or API key was blank)
        print("\nPlease login to CloudDefense to continue.")
        username = prompt_fn("Username (email): ").strip()
        password = secret_prompt_fn("Password: ").strip()

        token = self._login(username, password)
        if token:
            self._session_token = token
            print("Login successful.")
        else:
            raise RuntimeError("Login failed. Please check your credentials.")

        # 3) If API key was blank, prompt now after successful login
        if not api_key:
            print("\nNow visit the QINA integration page to get your API key:")
            print("  https://console.clouddefenseai.com/integrations/qina")
            print("Copy the API key from the UI and paste it below.")
            api_key = prompt_fn("QINA API key: ").strip()
            if not api_key:
                raise RuntimeError("API key is required.")

        # 4) Verify API key (with token)
        team_id = self._verify_api_key(token, api_key)
        if not team_id:
            raise RuntimeError("API key verification failed.")
        self.config.set_api_key(api_key)
        self.config.set_team_id(team_id)

        return {"api_key": api_key, "team_id": team_id}

    def _login(self, username: str, password: str) -> Optional[str]:
        payload = {"username": username, "password": password}
        _debug(f"POST {LOGIN_URL} (base={get_api_base_url()})")
        try:
            resp = requests.post(
                LOGIN_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            _debug(f"Login response status: {resp.status_code}")
            if 200 <= resp.status_code < 300:
                data = resp.json() if resp.content else {}
                _debug(f"Login response keys: {list(data.keys())}")
                token = (
                    (data.get("idtoken") or {}).get("access_token") or
                    (data.get("data") or {}).get("access_token") or
                    ((data.get("data") or {}).get("idtoken") or {}).get("access_token") or
                    data.get("access_token") or
                    data.get("token")
                )
                return token
            else:
                try:
                    err = resp.text[:300]
                    print(f"Login error {resp.status_code}: {err}")
                except Exception:
                    pass
                return None
        except Exception as exc:
            _debug(f"Login request failed: {exc}")
            return None

    def _verify_api_key(self, token: Optional[str], api_key: str) -> Optional[str]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        body = {"apiKey": api_key}
        _debug(f"POST {VERIFY_URL} (token={'yes' if token else 'no'})")
        try:
            resp = requests.post(VERIFY_URL, headers=headers, json=body, timeout=20)
            _debug(f"Verify response status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                # Expect the team id in response (handle multiple shapes)
                team_id = (
                    data.get("team_id") or
                    data.get("teamId") or
                    ((data.get("team") or {}).get("id")) or
                    ((data.get("data") or {}).get("teamId")) or
                    ((data.get("data") or {}).get("team_id"))
                )
                team_id = str(team_id).strip() if team_id is not None else ""
                return team_id or None
            return None
        except Exception:
            return None

    def handle_invalid_api_key(self):
        # Clear config to force re-login next run
        self.config.clear_all()

    def get_session_token(self, prompt_fn=input, secret_prompt_fn=input) -> str:
        """Return an access token, prompting the user to login if needed."""
        if self._session_token:
            return self._session_token

        print("\nAuthentication required. Please login to continue.")
        username = prompt_fn("Username (email): ").strip()
        password = secret_prompt_fn("Password: ").strip()

        token = self._login(username, password)
        if not token:
            raise RuntimeError("Login failed. Unable to obtain access token.")

        self._session_token = token
        print("Login successful.")
        return token


