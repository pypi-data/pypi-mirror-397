from typing import Protocol

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtBoundSignal
from pyqtgraph.parametertree import Parameter


class ConfigurationProtocol(Protocol):
    sig_file_changed: pyqtBoundSignal
    sig_expid_changed: pyqtBoundSignal
    sig_autoload_changed: pyqtBoundSignal
    sig_save_config: pyqtBoundSignal
    sig_parameter_changed: pyqtBoundSignal

    button_reload: QtWidgets.QPushButton
    button_save_cfg: QtWidgets.QPushButton

    file_parameters: Parameter
    param_parameters: Parameter
    settings_parameters: Parameter

    parameters_to_parse: list[str]

    def get_numbers_from_text(self, value: str | list | tuple) -> list[float] | str: ...
    def disable_buttons(self): ...
    def enable_buttons(self): ...
