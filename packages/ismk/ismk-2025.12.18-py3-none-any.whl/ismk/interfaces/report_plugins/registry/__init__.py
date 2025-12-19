__author__ = "Johannes Köster"
__copyright__ = "Copyright 2023, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import types
from typing import Mapping
from ismk.interfaces.report_plugins.registry.plugin import Plugin

from ismk.interfaces.report_plugins.settings import (
    ReportSettingsBase,
)
from ismk.interfaces.common.plugin_registry.attribute_types import (
    AttributeKind,
    AttributeMode,
    AttributeType,
)
from ismk.interfaces.common.plugin_registry import PluginRegistryBase
from ismk.interfaces.report_plugins import common
from ismk.interfaces.report_plugins.reporter import ReporterBase


class ReportPluginRegistry(PluginRegistryBase):
    """This class is a singleton that holds all registered report plugins."""

    @property
    def module_prefix(self) -> str:
        return common.report_plugin_module_prefix

    def load_plugin(self, name: str, module: types.ModuleType) -> Plugin:
        """Load a plugin by name."""
        return Plugin(
            _name=name,
            reporter=module.Reporter,
            _report_settings_cls=getattr(module, "ReportSettings", None),
        )

    def expected_attributes(self) -> Mapping[str, AttributeType]:
        return {
            "ReportSettings": AttributeType(
                cls=ReportSettingsBase,
                mode=AttributeMode.OPTIONAL,
                kind=AttributeKind.CLASS,
            ),
            "Reporter": AttributeType(
                cls=ReporterBase,
                mode=AttributeMode.REQUIRED,
                kind=AttributeKind.CLASS,
            ),
        }

    def collect_plugins(self):
        """Collect plugins and call register_plugin for each."""
        super().collect_plugins()

        try:
            from ismk.report import html_reporter
        except ImportError:
            # ismk not present, proceed without adding builtin plugins
            return

        self.register_plugin("html", html_reporter)
