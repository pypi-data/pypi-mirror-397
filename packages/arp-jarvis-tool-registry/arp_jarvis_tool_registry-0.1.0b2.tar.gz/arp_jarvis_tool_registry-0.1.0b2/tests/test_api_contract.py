import unittest

from tool_registry.catalog import ToolCatalog, load_domain_tools  # noqa: E402
from tool_registry.server import ToolRegistryApp  # noqa: E402


class TestToolRegistryApiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        catalog = ToolCatalog(load_domain_tools(["core"]))
        cls._app = ToolRegistryApp(catalog)

    @classmethod
    def tearDownClass(cls) -> None:
        return

    def test_health(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1alpha1/health", body=None)
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(set(body.keys()), {"status", "time"})
        self.assertIn(body["status"], {"ok", "degraded", "down"})
        self.assertIsInstance(body["time"], str)

    def test_version(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1alpha1/version", body=None)
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(set(body.keys()), {"service_name", "service_version", "supported_api_versions"})
        self.assertIsInstance(body["service_name"], str)
        self.assertIsInstance(body["service_version"], str)
        self.assertIsInstance(body["supported_api_versions"], list)
        self.assertIn("v1alpha1", body["supported_api_versions"])

    def test_list_tools_returns_tool_definitions(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1alpha1/tools", body=None)
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, list)
        tool_ids = set()
        for item in body:
            self.assertIsInstance(item, dict)
            self.assertIn("tool_id", item)
            self.assertIn("name", item)
            self.assertIn("input_schema", item)
            self.assertIn("source", item)
            self.assertIsInstance(item["tool_id"], str)
            self.assertIsInstance(item["name"], str)
            self.assertIsInstance(item["input_schema"], dict)
            self.assertIsInstance(item["source"], str)
            tool_ids.add(item["tool_id"])
        self.assertTrue({"tool_echo", "tool_calc", "tool_time_now"}.issubset(tool_ids))

    def test_get_tool_definition(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1alpha1/tools/tool_echo", body=None)
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("tool_id"), "tool_echo")
        self.assertEqual(body.get("name"), "echo")
        self.assertIn("input_schema", body)
        self.assertIsInstance(body["input_schema"], dict)

    def test_invoke_ok(self) -> None:
        status, body, _ = self._app.handle(
            method="POST",
            path="/v1alpha1/tool-invocations",
            body={"invocation_id": "inv_1", "tool_id": "tool_echo", "args": {"text": "hi"}},
        )
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("invocation_id"), "inv_1")
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("result", {}).get("text"), "hi")
        self.assertIsInstance(body.get("duration_ms"), int)

    def test_invoke_invalid_args(self) -> None:
        status, body, _ = self._app.handle(
            method="POST",
            path="/v1alpha1/tool-invocations",
            body={"invocation_id": "inv_2", "tool_id": "tool_echo", "args": {}},
        )
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertFalse(body.get("ok"))
        self.assertEqual(body.get("invocation_id"), "inv_2")
        self.assertEqual(body.get("error", {}).get("code"), "tool.invalid_args")
        issues = body.get("error", {}).get("details", {}).get("issues")
        self.assertIsInstance(issues, list)
        self.assertGreaterEqual(len(issues), 1)
        self.assertIsInstance(body.get("duration_ms"), int)

    def test_invoke_unknown_tool(self) -> None:
        status, body, _ = self._app.handle(
            method="POST",
            path="/v1alpha1/tool-invocations",
            body={"invocation_id": "inv_3", "tool_id": "tool_nope", "args": {}},
        )
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertFalse(body.get("ok"))
        self.assertEqual(body.get("invocation_id"), "inv_3")
        self.assertEqual(body.get("error", {}).get("code"), "tool.not_found")

    def test_invoke_invalid_json(self) -> None:
        status, body, _ = self._app.handle(method="POST", path="/v1alpha1/tool-invocations", body=None)
        self.assertEqual(int(status), 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("error", {}).get("code"), "request.invalid_json")

    def test_route_not_found(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1alpha1/nope", body=None)
        self.assertEqual(int(status), 404)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("error", {}).get("code"), "route.not_found")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
