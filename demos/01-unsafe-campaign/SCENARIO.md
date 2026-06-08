# Scenario: Phishing campaign without safety rails

Someone set up a 'test' campaign without consent docs, training, or even external-banner pre-checks.

## Expected findings

- PF-NOAUTH-001 (no training URL)
- PF-NOCONS-001 (no consent record)
- PF-BANNER-001 (external banner not configured)

## Why this matters

These are legal pre-reqs. Running phishing without them invites HR complaints and possible state-law CFAA issues.
