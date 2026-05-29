import io
import json
import os
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock

from brandsearch_cli import cli


class BrandsearchCLITest(unittest.TestCase):
    def run_cli(self, args, env=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        old_env = os.environ.copy()
        os.environ.clear()
        os.environ.update(env or {})
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = cli.main(args)
            return code, stdout.getvalue(), stderr.getvalue()
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_brief_outputs_json(self):
        code, out, err = self.run_cli(["--brief"])
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertTrue(payload["ok"])
        self.assertIn("Brandsearch CLI", payload["data"]["brief"])

    def test_secret_argument_rejected(self):
        code, out, err = self.run_cli(["lookup", "--q", "bsk_realbad"])
        self.assertEqual(code, 2)
        payload = json.loads(err)
        self.assertEqual(payload["code"], "SECRET_IN_ARGS")

    def test_missing_key_for_account_is_auth_error(self):
        code, out, err = self.run_cli(["account", "me"])
        self.assertEqual(code, 10)
        payload = json.loads(err)
        self.assertEqual(payload["code"], "MISSING_API_KEY")

    def test_discover_blocks_without_approval(self):
        code, out, err = self.run_cli(["brands", "discover", "--limit", "5"], {"BRANDSEARCH_API_KEY": "bsk_test"})
        self.assertEqual(code, 30)
        payload = json.loads(err)
        self.assertEqual(payload["code"], "METERED_APPROVAL_REQUIRED")

    def test_discover_dry_run_no_key_no_network(self):
        with mock.patch.object(cli, "request_json") as req:
            code, out, err = self.run_cli(["brands", "discover", "--dry-run", "--limit", "5", "--niche", "Beauty & Skincare"])
            self.assertEqual(code, 0, err)
            req.assert_not_called()
            payload = json.loads(out)
            self.assertEqual(payload["data"]["estimated_credits"], 5)
            self.assertTrue(payload["data"]["metered"])

    def test_health_uses_public_endpoint(self):
        fake = cli.APIResponse(200, {"x-quota-charged": "false"}, {"status": "ok"})
        with mock.patch.object(cli, "request_json", return_value=fake) as req:
            code, out, err = self.run_cli(["health"])
            self.assertEqual(code, 0, err)
            req.assert_called_once_with("/health", auth=False)
            payload = json.loads(out)
            self.assertEqual(payload["data"]["status"], "ok")

    def test_facets_calls_expected_path(self):
        fake = cli.APIResponse(200, {"x-quota-charged": "false"}, ["Beauty & Skincare"])
        with mock.patch.object(cli, "request_json", return_value=fake) as req:
            code, out, err = self.run_cli(["facets", "niches"], {"BRANDSEARCH_API_KEY": "bsk_test"})
            self.assertEqual(code, 0, err)
            req.assert_called_once_with("/v1/facets/niches")
            payload = json.loads(out)
            self.assertIn("Beauty & Skincare", payload["data"])

    def test_lookup_limit_validation(self):
        code, out, err = self.run_cli(["lookup", "--q", "x", "--limit", "100"], {"BRANDSEARCH_API_KEY": "bsk_test"})
        self.assertEqual(code, 2)
        payload = json.loads(err)
        self.assertEqual(payload["code"], "INVALID_LIMIT")


if __name__ == "__main__":
    unittest.main()
