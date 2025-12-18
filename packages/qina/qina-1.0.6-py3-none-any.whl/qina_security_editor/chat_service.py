#!/usr/bin/env python3
"""
Chat Service for QINA Security Editor
Handles retrieval of scan context and asking bot questions from the terminal.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List

import requests

from .config_manager import ConfigManager


class ChatService:
    """Facade for CloudDefense bot endpoint."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_base = self.config.get_api_base_url()

    def _get_scan_details(self, cli_id: str, api_key: str) -> Dict[str, Any]:
        """Fetch scan details required for chat payload."""
        url = f"{self.api_base}/api/ide/file/scan-details/{cli_id}"
        headers = {"X-API-Key": api_key}
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json() if resp.content else {}
            return data or {}
        except Exception as exc:
            raise RuntimeError(f"Failed to load scan context: {exc}") from exc

    def _build_payload(
        self,
        question: str,
        team_id: str,
        scan_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compose the payload for the bot question endpoint."""
        def _ensure_int_list(values: Optional[List[Any]]) -> List[int]:
            safe_values = values or []
            normalized = []
            for value in safe_values:
                try:
                    normalized.append(int(value))
                except (TypeError, ValueError):
                    continue
            return normalized

        payload = {
            "question": question,
            "teamIds": [int(team_id)] if team_id else [],
            "applicationIds": _ensure_int_list(scan_details.get("applicationIds")),
            "scanHistoryId": (
                int(scan_details.get("scanHistoryId"))
                if scan_details.get("scanHistoryId") is not None
                else None
            ),
            "scanInstanceIds": _ensure_int_list(scan_details.get("scanInstanceIds")),
        }
        # Remove keys with None to avoid API validation errors
        return {k: v for k, v in payload.items() if v not in (None, [], "")}

    def ask_question(
        self,
        question: str,
        api_key: str,
        team_id: str,
        cli_id: str,
    ) -> Dict[str, Any]:
        """Ask the CloudDefense bot a question using current scan context."""
        question = (question or "").strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        scan_details = self._get_scan_details(cli_id, api_key)
        if not scan_details:
            raise RuntimeError("No scan details available for this CLI session.")

        payload = self._build_payload(question, team_id, scan_details)

        url = f"{self.api_base}/api/ide/bot/question"
        headers = {
            "Content-Type": "application/json",
            "CLOUDDEFENSE_API_KEY": api_key,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp.json() if resp.content else {"message": "No content"}
        except Exception as exc:
            raise RuntimeError(f"Chat request failed: {exc}") from exc

