from django.test import TestCase
from unittest.mock import patch, MagicMock

from plugin.manager import plugin_manager


class TestWhiteboxPluginDemoMode(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginDemoMode"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "Demo Mode")

    def test_service_component_exposed(self):
        exposed_component_map = self.plugin.get_exposed_component_map()
        self.assertIn("service-component", exposed_component_map)
        self.assertIn("demo-mode", exposed_component_map["service-component"])
        self.assertEqual(
            exposed_component_map["service-component"]["demo-mode"],
            "DemoModeServiceComponent",
        )
