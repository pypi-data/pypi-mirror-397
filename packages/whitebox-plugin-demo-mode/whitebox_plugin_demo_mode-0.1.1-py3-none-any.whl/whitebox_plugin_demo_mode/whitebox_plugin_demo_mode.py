import whitebox


class WhiteboxPluginDemoMode(whitebox.Plugin):
    name = "Demo Mode"

    exposed_component_map = {
        "service-component": {
            "demo-mode": "DemoModeServiceComponent",
        },
    }


plugin_class = WhiteboxPluginDemoMode
