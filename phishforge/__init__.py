"""PHISHFORGE - open-source phishing simulation for blue teams.

Manage simulated phishing campaigns: render templates, generate per-recipient
tracking tokens, simulate recipient events (sent/opened/clicked/reported), and
score campaign + user susceptibility for security-awareness training.

For authorized internal security training only.
"""
from .core import (
    Campaign,
    Recipient,
    Template,
    render_template,
    make_token,
    risk_band,
    campaign_report,
    user_scores,
    record_event,
    EVENT_WEIGHTS,
    EVENTS,
)

TOOL_NAME = "phishforge"
TOOL_VERSION = "1.0.0"

__all__ = [
    "Campaign",
    "Recipient",
    "Template",
    "render_template",
    "make_token",
    "risk_band",
    "campaign_report",
    "user_scores",
    "record_event",
    "EVENT_WEIGHTS",
    "EVENTS",
    "TOOL_NAME",
    "TOOL_VERSION",
]
