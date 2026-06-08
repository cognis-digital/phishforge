"""Smoke tests for PHISHFORGE. No network. stdlib unittest."""
import io
import json
import os
import unittest
from contextlib import redirect_stdout

from phishforge import (
    Campaign,
    Recipient,
    Template,
    TOOL_NAME,
    TOOL_VERSION,
    campaign_report,
    make_token,
    record_event,
    render_template,
    risk_band,
    user_scores,
)
from phishforge.cli import main

HERE = os.path.dirname(__file__)
DEMO = os.path.join(HERE, os.pardir, "demos", "01-basic")
TEMPLATE = os.path.join(DEMO, "template.json")
RECIPIENTS = os.path.join(DEMO, "recipients.csv")


def _tmpl():
    return Template("t", "Hi {{first_name}}", "Go to {{tracking_url}} now {{unknown}}")


class CoreTests(unittest.TestCase):
    def test_meta(self):
        self.assertEqual(TOOL_NAME, "phishforge")
        self.assertTrue(TOOL_VERSION)

    def test_token_deterministic_and_scoped(self):
        a = make_token("s", "camp", "x@y.test")
        self.assertEqual(a, make_token("s", "camp", "x@y.test"))
        self.assertNotEqual(a, make_token("s", "OTHER", "x@y.test"))
        self.assertNotEqual(a, make_token("other", "camp", "x@y.test"))
        self.assertEqual(len(a), 16)

    def test_render_substitutes_and_keeps_unknown(self):
        r = Recipient("jane.doe@acme.test", "Jane Doe", "Sales")
        out = render_template(_tmpl(), r, campaign="c", secret="s")
        self.assertIn("Jane", out["subject"])
        self.assertIn(out["token"], out["body"])
        self.assertIn("{{unknown}}", out["body"])  # unknown left intact

    def test_template_placeholders(self):
        self.assertEqual(_tmpl().placeholders(), ["first_name", "tracking_url", "unknown"])

    def test_record_event_and_scores(self):
        camp = Campaign("c", _tmpl(), [Recipient("a@b.test")])
        record_event(camp, "a@b.test", "opened")
        record_event(camp, "a@b.test", "clicked")
        rows = user_scores(camp)
        self.assertEqual(rows[0]["score"], 6)
        self.assertEqual(rows[0]["risk"], "medium")

    def test_reported_is_protective(self):
        self.assertEqual(risk_band(-4), "safe")
        self.assertEqual(risk_band(10), "high")

    def test_record_event_validation(self):
        camp = Campaign("c", _tmpl(), [Recipient("a@b.test")])
        with self.assertRaises(ValueError):
            record_event(camp, "a@b.test", "bogus")
        with self.assertRaises(KeyError):
            record_event(camp, "nobody@b.test", "opened")

    def test_campaign_report_funnel(self):
        camp = Campaign("c", _tmpl(),
                        [Recipient("a@b.test"), Recipient("c@d.test")])
        record_event(camp, "a@b.test", "opened")
        record_event(camp, "a@b.test", "clicked")
        rep = campaign_report(camp)
        self.assertEqual(rep["recipients"], 2)
        self.assertEqual(rep["counts"]["sent"], 2)
        self.assertEqual(rep["counts"]["clicked"], 1)
        self.assertEqual(rep["rates_pct"]["click"], 50.0)


class CliTests(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        return rc, buf.getvalue()

    def test_report_json(self):
        rc, out = self._run([
            "--format", "json", "report",
            "--template", TEMPLATE, "--recipients", RECIPIENTS,
            "--campaign", "q2",
            "--event", "bob@acme.test=opened",
            "--event", "bob@acme.test=clicked",
            "--event", "bob@acme.test=submitted",
            "--event", "carol@acme.test=reported",
        ])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["recipients"], 4)
        self.assertEqual(data["counts"]["submitted"], 1)
        self.assertEqual(data["risk_bands"]["high"], 1)  # bob = 16

    def test_render_and_token(self):
        rc, out = self._run([
            "--format", "json", "token",
            "--template", TEMPLATE, "--recipients", RECIPIENTS,
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(len(json.loads(out)["tokens"]), 4)

    def test_missing_file_nonzero(self):
        rc, _ = self._run([
            "report", "--template", "nope.json", "--recipients", RECIPIENTS,
        ])
        self.assertEqual(rc, 1)

    def test_bad_event_nonzero(self):
        rc, _ = self._run([
            "report", "--template", TEMPLATE, "--recipients", RECIPIENTS,
            "--event", "bob@acme.test=explode",
        ])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
