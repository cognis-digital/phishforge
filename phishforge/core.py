"""Core phishing-simulation engine. Standard library only."""
from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

# Ordered event funnel. Each later stage implies a higher-risk action.
EVENTS = ("sent", "opened", "clicked", "submitted", "reported")

# Susceptibility weight per event. "reported" is protective (negative).
EVENT_WEIGHTS: Dict[str, int] = {
    "sent": 0,
    "opened": 1,
    "clicked": 5,
    "submitted": 10,
    "reported": -4,
}

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")


@dataclass
class Template:
    """A phishing email template with {{placeholder}} substitution."""

    name: str
    subject: str
    body: str

    def placeholders(self) -> List[str]:
        found = []
        for src in (self.subject, self.body):
            for m in _PLACEHOLDER.finditer(src):
                if m.group(1) not in found:
                    found.append(m.group(1))
        return found


@dataclass
class Recipient:
    """A campaign target."""

    email: str
    name: str = ""
    department: str = ""

    def fields(self) -> Dict[str, str]:
        local = self.email.split("@", 1)[0]
        return {
            "email": self.email,
            "name": self.name or local,
            "first_name": (self.name or local).split(" ")[0],
            "department": self.department,
        }


@dataclass
class Campaign:
    """A phishing simulation campaign and its recorded events."""

    name: str
    template: Template
    recipients: List[Recipient] = field(default_factory=list)
    secret: str = "phishforge"
    # email -> list of recorded events (in order recorded)
    events: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for r in self.recipients:
            self.events.setdefault(r.email, [])


def _validate_email(email: str) -> str:
    email = (email or "").strip()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError(f"invalid email: {email!r}")
    return email


def make_token(secret: str, campaign: str, email: str) -> str:
    """Deterministic per-recipient tracking token (HMAC-SHA256, 16 hex)."""
    msg = f"{campaign}\x00{email}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:16]


def render_template(template: Template, recipient: Recipient, *,
                    base_url: str = "https://sim.example.com",
                    secret: str = "phishforge",
                    campaign: str = "campaign") -> Dict[str, str]:
    """Render subject/body for a recipient, substituting placeholders.

    Adds a {{tracking_url}} field carrying the recipient's token. Unknown
    placeholders are left intact so authors can spot mistakes.
    """
    token = make_token(secret, campaign, recipient.email)
    fields = recipient.fields()
    fields["token"] = token
    fields["tracking_url"] = f"{base_url}/t/{token}"
    fields["campaign"] = campaign

    def sub(text: str) -> str:
        return _PLACEHOLDER.sub(
            lambda m: fields.get(m.group(1), m.group(0)), text
        )

    return {
        "email": recipient.email,
        "token": token,
        "subject": sub(template.subject),
        "body": sub(template.body),
    }


def record_event(campaign: Campaign, email: str, event: str) -> List[str]:
    """Record an event for a recipient. Returns that recipient's event list."""
    email = _validate_email(email)
    if event not in EVENT_WEIGHTS:
        raise ValueError(f"unknown event {event!r}; valid: {', '.join(EVENTS)}")
    if email not in campaign.events:
        raise KeyError(f"{email} is not a recipient of campaign {campaign.name!r}")
    campaign.events[email].append(event)
    return campaign.events[email]


def _user_score(events: Iterable[str]) -> int:
    return sum(EVENT_WEIGHTS.get(e, 0) for e in events)


def risk_band(score: int) -> str:
    """Map a susceptibility score to a training-priority band."""
    if score <= 0:
        return "safe"
    if score < 5:
        return "low"
    if score < 10:
        return "medium"
    return "high"


def user_scores(campaign: Campaign) -> List[Dict]:
    """Per-recipient susceptibility scores, highest risk first."""
    rows = []
    for email in sorted(campaign.events):
        evs = campaign.events[email]
        score = _user_score(evs)
        rows.append({
            "email": email,
            "events": list(evs),
            "score": score,
            "risk": risk_band(score),
            "reported": "reported" in evs,
        })
    rows.sort(key=lambda r: (-r["score"], r["email"]))
    return rows


def campaign_report(campaign: Campaign) -> Dict:
    """Aggregate funnel counts, rates, and risk distribution for a campaign."""
    total = len(campaign.events)
    counts = {e: 0 for e in EVENTS}
    for evs in campaign.events.values():
        seen = set(evs)
        for e in EVENTS:
            if e in seen:
                counts[e] += 1
    # Anyone with no recorded event still counts as a target that was sent to.
    counts["sent"] = max(counts["sent"], total)

    def rate(n: int) -> float:
        return round(100.0 * n / total, 1) if total else 0.0

    rows = user_scores(campaign)
    bands = {"safe": 0, "low": 0, "medium": 0, "high": 0}
    for r in rows:
        bands[r["risk"]] += 1

    return {
        "campaign": campaign.name,
        "template": campaign.template.name,
        "recipients": total,
        "counts": counts,
        "rates_pct": {
            "open": rate(counts["opened"]),
            "click": rate(counts["clicked"]),
            "submit": rate(counts["submitted"]),
            "report": rate(counts["reported"]),
        },
        "risk_bands": bands,
        "users": rows,
    }
