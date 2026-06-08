"""PHISHFORGE command-line interface (stdlib argparse only)."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List, Optional

from . import TOOL_NAME, TOOL_VERSION
from .core import (
    Campaign,
    Recipient,
    Template,
    campaign_report,
    make_token,
    record_event,
    render_template,
    user_scores,
    EVENTS,
)


def _load_recipients(path: str) -> List[Recipient]:
    out: List[Recipient] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "email" not in reader.fieldnames:
            raise ValueError("recipients CSV must have an 'email' column")
        for row in reader:
            email = (row.get("email") or "").strip()
            if not email:
                continue
            out.append(Recipient(
                email=email,
                name=(row.get("name") or "").strip(),
                department=(row.get("department") or "").strip(),
            ))
    if not out:
        raise ValueError(f"no recipients loaded from {path}")
    return out


def _load_template(path: str) -> Template:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for key in ("name", "subject", "body"):
        if key not in data:
            raise ValueError(f"template missing required key: {key!r}")
    return Template(name=data["name"], subject=data["subject"], body=data["body"])


def _build_campaign(args) -> Campaign:
    template = _load_template(args.template)
    recipients = _load_recipients(args.recipients)
    camp = Campaign(name=args.campaign, template=template,
                    recipients=recipients, secret=args.secret)
    if getattr(args, "events", None):
        for spec in args.events:
            email, _, event = spec.partition("=")
            record_event(camp, email.strip(), event.strip())
    return camp


def _emit(payload, fmt: str, table_fn) -> None:
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        table_fn(payload)


def _print_render(payload) -> None:
    for row in payload["rendered"]:
        print(f"--- {row['email']}  (token {row['token']}) ---")
        print(f"Subject: {row['subject']}")
        print(row["body"])
        print()


def _print_report(rep) -> None:
    print(f"Campaign : {rep['campaign']}  (template: {rep['template']})")
    print(f"Targets  : {rep['recipients']}")
    c, r = rep["counts"], rep["rates_pct"]
    print(f"  opened   : {c['opened']:>4}  ({r['open']}%)")
    print(f"  clicked  : {c['clicked']:>4}  ({r['click']}%)")
    print(f"  submitted: {c['submitted']:>4}  ({r['submit']}%)")
    print(f"  reported : {c['reported']:>4}  ({r['report']}%)")
    b = rep["risk_bands"]
    print(f"Risk     : high={b['high']} medium={b['medium']} "
          f"low={b['low']} safe={b['safe']}")


def _print_score(rows) -> None:
    print(f"{'EMAIL':<32} {'SCORE':>5}  {'RISK':<7} EVENTS")
    for r in rows["users"]:
        print(f"{r['email']:<32} {r['score']:>5}  {r['risk']:<7} "
              f"{','.join(r['events']) or '-'}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="PHISHFORGE - phishing simulation for security-awareness "
                    "training (authorized internal use only).",
    )
    p.add_argument("--version", action="version",
                   version=f"{TOOL_NAME} {TOOL_VERSION}")
    p.add_argument("--format", choices=("table", "json"), default="table",
                   help="output format (default: table)")
    sub = p.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--template", required=True, help="template JSON file")
    common.add_argument("--recipients", required=True, help="recipients CSV file")
    common.add_argument("--campaign", default="campaign", help="campaign name")
    common.add_argument("--secret", default="phishforge",
                        help="HMAC secret for tracking tokens")

    pr = sub.add_parser("render", parents=[common],
                        help="render the template for every recipient")
    pr.add_argument("--base-url", default="https://sim.example.com",
                    help="base URL for tracking links")

    sub.add_parser("token", parents=[common],
                   help="print the tracking token for every recipient")

    pe = argparse.ArgumentParser(add_help=False)
    pe.add_argument("--event", dest="events", action="append", default=[],
                    metavar="EMAIL=EVENT",
                    help=f"record an event ({'/'.join(EVENTS)}); repeatable")

    sub.add_parser("report", parents=[common, pe],
                   help="funnel + risk-band report for a campaign")
    sub.add_parser("score", parents=[common, pe],
                   help="per-recipient susceptibility scores")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        cmd = args.command
        if cmd == "render":
            camp = _build_campaign(args)
            rendered = [
                render_template(camp.template, r, base_url=args.base_url,
                                secret=camp.secret, campaign=camp.name)
                for r in camp.recipients
            ]
            _emit({"campaign": camp.name, "rendered": rendered},
                  args.format, _print_render)
        elif cmd == "token":
            camp = _build_campaign(args)
            toks = [{"email": r.email,
                     "token": make_token(camp.secret, camp.name, r.email)}
                    for r in camp.recipients]
            _emit({"campaign": camp.name, "tokens": toks}, args.format,
                  lambda p: [print(f"{t['token']}  {t['email']}")
                             for t in p["tokens"]])
        elif cmd == "report":
            camp = _build_campaign(args)
            _emit(campaign_report(camp), args.format, _print_report)
        elif cmd == "score":
            camp = _build_campaign(args)
            _emit({"campaign": camp.name, "users": user_scores(camp)},
                  args.format, _print_score)
        else:  # pragma: no cover - argparse enforces choices
            parser.error(f"unknown command {cmd!r}")
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
