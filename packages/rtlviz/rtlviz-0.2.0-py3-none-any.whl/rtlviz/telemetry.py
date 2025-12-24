"""
RTLViz Telemetry - Privacy-Protected Usage Analytics

This module sends anonymous usage pings to help improve RTLViz.
NO personal data, file contents, or identifying information is collected.

What IS collected:
- Event type (session_start, render)
- RTLViz version
- Random session ID (not tied to user)

What is NOT collected:
- IP addresses
- File paths or contents
- User names or machine names
- Any RTL/Verilog code
- Operating system details

Users can opt-out by setting: RTLVIZ_TELEMETRY=0
"""

import os
import uuid
import threading
from typing import Optional

# Telemetry endpoint - Google Apps Script webhook
# Replace with your deployed webhook URL
TELEMETRY_ENDPOINT = os.environ.get(
    "RTLVIZ_TELEMETRY_URL",
    "https://script.google.com/macros/s/AKfycbxJiF7kJuUNYXwJbsn2x8jTlXW-w3-nhoh4y344U2YtCm9y4yCSiptVq1rPkLbqzjOC7Q/exec"
)

# Version
VERSION = "0.2.0"

# Persistent session ID for this run (regenerated each server start)
_SESSION_ID: Optional[str] = None


def _get_session_id() -> str:
    """Get or create a session ID for this run."""
    global _SESSION_ID
    if _SESSION_ID is None:
        _SESSION_ID = str(uuid.uuid4())[:8]  # Short random ID
    return _SESSION_ID


def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled (opt-out via env var)."""
    return os.environ.get("RTLVIZ_TELEMETRY", "1").lower() not in ("0", "false", "no", "off")


def _send_ping(event: str) -> None:
    """Send a telemetry ping in the background (non-blocking)."""
    if not is_telemetry_enabled():
        return
    
    # Skip if using placeholder URL
    if "YOUR_DEPLOYMENT_ID" in TELEMETRY_ENDPOINT:
        return
    
    def _do_send():
        try:
            import urllib.request
            import json
            
            payload = {
                "event": event,
                "version": VERSION,
                "session_id": _get_session_id(),
                "token": "rtlviz-analytics-v1-keep-safe"  # Must match Google Script
            }
            
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                TELEMETRY_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            # Short timeout, don't block
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            # Silently ignore all errors - telemetry should never break the app
            pass
    
    # Run in background thread so it doesn't slow down the server
    thread = threading.Thread(target=_do_send, daemon=True)
    thread.start()


def ping_session_start() -> None:
    """Ping when the server starts."""
    _send_ping("session_start")


def ping_diagram_rendered(success: bool = True) -> None:
    """Ping when a diagram is rendered."""
    _send_ping("render")
