# Demo 01 - Basic IT Password-Reset Simulation

A blue-team analyst runs an authorized phishing-awareness exercise against the
Engineering and Finance departments using a fake "IT password expiry" lure.

## Inputs

- `template.json` - the lure email with `{{first_name}}`, `{{department}}`, and
  `{{tracking_url}}` placeholders.
- `recipients.csv` - four targets (email, name, department).

## 1. Render per-recipient emails (with unique tracking tokens)

```bash
python -m phishforge render \
  --template demos/01-basic/template.json \
  --recipients demos/01-basic/recipients.csv \
  --campaign q2-password-reset \
  --secret s3cr3t
```

Each recipient gets a deterministic HMAC tracking token, so the same recipient
in the same campaign always resolves to the same `/t/<token>` link.

## 2. Record what happened, then score susceptibility

Events (in funnel order): `sent`, `opened`, `clicked`, `submitted`, `reported`.
Reporting the email is protective and lowers a user's risk score.

```bash
python -m phishforge report \
  --template demos/01-basic/template.json \
  --recipients demos/01-basic/recipients.csv \
  --campaign q2-password-reset \
  --event alice@acme.test=opened \
  --event bob@acme.test=opened \
  --event bob@acme.test=clicked \
  --event bob@acme.test=submitted \
  --event carol@acme.test=reported \
  --format json
```

`report` shows the open/click/submit/report funnel and the high/medium/low/safe
risk distribution. `score` ranks individual users so training can be targeted at
the people who actually submitted credentials.

> For authorized internal security training only.
