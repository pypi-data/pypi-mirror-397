__author__ = "Johannes Köster"
__copyright__ = "Copyright 2024, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass


import ismk.interfaces.common.plugin_registry.plugin


@dataclass
class ReportSettingsBase(ismk.interfaces.common.plugin_registry.plugin.SettingsBase):
    pass
