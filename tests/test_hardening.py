"""Hardening tests — error paths, edge cases, and input validation.

These tests verify graceful failure: missing files, malformed input,
invalid arguments, and empty collections.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from phishforge import (
    Campaign,
    Recipient,
    Template,
    make_token,
    render_template,
    campaign_report,
    user_scores,
)
from phishforge.cli import main

HERE = os.path.dirname(__file__)
DEMO = os.path.join(HERE, os.pardir, "demos", "01-basic")
TEMPLATE = os.path.join(DEMO, "template.json")
RECIPIENTS = os.path.join(DEMO, "recipients.csv")


def _run(argv):
    """Run main(), capturing stdout and stderr, returning (rc, stdout, stderr)."""
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        rc = main(argv)
    return rc, out_buf.getvalue(), err_buf.getvalue()


# ---------------------------------------------------------------------------
# core.make_token validation
# ---------------------------------------------------------------------------
class TestMakeTokenValidation(unittest.TestCase):
    def test_empty_secret_raises(self):
        with self.assertRaises(ValueError):
            make_token("", "camp", "a@b.test")

    def test_empty_campaign_raises(self):
        with self.assertRaises(ValueError):
            make_token("s", "", "a@b.test")

    def test_empty_email_raises(self):
        with self.assertRaises(ValueError):
            make_token("s", "camp", "")


# ---------------------------------------------------------------------------
# CLI: missing and malformed files
# ---------------------------------------------------------------------------
class TestMissingFiles(unittest.TestCase):
    def test_missing_template_exits_nonzero(self):
        rc, _, err = _run([
            "report", "--template", "nonexistent_template.json",
            "--recipients", RECIPIENTS,
        ])
        self.assertNotEqual(rc, 0)
        self.assertIn("error", err.lower())

    def test_missing_recipients_exits_nonzero(self):
        rc, _, err = _run([
            "report", "--template", TEMPLATE,
            "--recipients", "nonexistent_recipients.csv",
        ])
        self.assertNotEqual(rc, 0)
        self.assertIn("error", err.lower())

    def test_missing_template_exits_1(self):
        rc, _, _ = _run([
            "report", "--template", "no_such_file.json",
            "--recipients", RECIPIENTS,
        ])
        self.assertEqual(rc, 1)

    def test_missing_recipients_exits_1(self):
        rc, _, _ = _run([
            "report", "--template", TEMPLATE,
            "--recipients", "no_such_file.csv",
        ])
        self.assertEqual(rc, 1)


class TestMalformedTemplateJSON(unittest.TestCase):
    def test_invalid_json_exits_nonzero(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{ not valid json }")
            tmppath = f.name
        try:
            rc, _, err = _run([
                "report", "--template", tmppath,
                "--recipients", RECIPIENTS,
            ])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.lower())
        finally:
            os.unlink(tmppath)

    def test_missing_required_key_exits_nonzero(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"name": "t", "subject": "Hi"}, f)  # missing 'body'
            tmppath = f.name
        try:
            rc, _, err = _run([
                "report", "--template", tmppath,
                "--recipients", RECIPIENTS,
            ])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.lower())
        finally:
            os.unlink(tmppath)

    def test_non_object_json_exits_nonzero(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump([1, 2, 3], f)
            tmppath = f.name
        try:
            rc, _, err = _run([
                "report", "--template", tmppath,
                "--recipients", RECIPIENTS,
            ])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.lower())
        finally:
            os.unlink(tmppath)


class TestMalformedRecipientsCSV(unittest.TestCase):
    def test_missing_email_column_exits_nonzero(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as f:
            f.write("name,department\nAlice,Eng\n")
            tmppath = f.name
        try:
            rc, _, err = _run([
                "report", "--template", TEMPLATE,
                "--recipients", tmppath,
            ])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.lower())
        finally:
            os.unlink(tmppath)

    def test_empty_csv_exits_nonzero(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as f:
            f.write("email,name,department\n")  # header only, no data rows
            tmppath = f.name
        try:
            rc, _, err = _run([
                "report", "--template", TEMPLATE,
                "--recipients", tmppath,
            ])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.lower())
        finally:
            os.unlink(tmppath)

    def test_all_blank_emails_exits_nonzero(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as f:
            f.write("email,name\n,Alice\n  ,Bob\n")
            tmppath = f.name
        try:
            rc, _, err = _run([
                "report", "--template", TEMPLATE,
                "--recipients", tmppath,
            ])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.lower())
        finally:
            os.unlink(tmppath)


# ---------------------------------------------------------------------------
# CLI: malformed --event argument
# ---------------------------------------------------------------------------
class TestEventArgValidation(unittest.TestCase):
    def test_event_missing_equals_exits_nonzero(self):
        rc, _, err = _run([
            "report", "--template", TEMPLATE,
            "--recipients", RECIPIENTS,
            "--event", "bob@acme.testopened",  # no '='
        ])
        self.assertNotEqual(rc, 0)
        self.assertIn("error", err.lower())


# ---------------------------------------------------------------------------
# core edge cases
# ---------------------------------------------------------------------------
class TestCoreEdgeCases(unittest.TestCase):
    def test_campaign_report_no_events(self):
        """campaign_report on a campaign with zero events should not raise."""
        camp = Campaign(
            "c",
            Template("t", "subj", "body"),
            [Recipient("x@y.test")],
        )
        rep = campaign_report(camp)
        self.assertEqual(rep["recipients"], 1)
        self.assertEqual(rep["rates_pct"]["open"], 0.0)
        self.assertEqual(rep["rates_pct"]["click"], 0.0)

    def test_user_scores_empty_recipients(self):
        """user_scores on a campaign with no recipients returns an empty list."""
        camp = Campaign("c", Template("t", "s", "b"), [])
        self.assertEqual(user_scores(camp), [])

    def test_render_template_no_placeholders(self):
        """render_template on a template with no placeholders works fine."""
        tmpl = Template("plain", "Hello", "No substitution here.")
        r = Recipient("z@test.example")
        out = render_template(tmpl, r, campaign="c", secret="s")
        self.assertEqual(out["subject"], "Hello")
        self.assertEqual(out["body"], "No substitution here.")

    def test_render_template_email_only_recipient(self):
        """Recipient with only email (no name/dept) renders without error."""
        tmpl = Template("t", "Hi {{name}}", "Dept: {{department}}")
        r = Recipient("noname@test.example")
        out = render_template(tmpl, r, campaign="c", secret="s")
        # name falls back to local part of email
        self.assertIn("noname", out["subject"])
        # department is empty string
        self.assertIn("Dept:", out["body"])


if __name__ == "__main__":
    unittest.main()
