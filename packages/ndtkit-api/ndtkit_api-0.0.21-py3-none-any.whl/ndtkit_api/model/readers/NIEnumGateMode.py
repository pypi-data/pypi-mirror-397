"""Python wrapper for agi.ndtkit.api.model.readers.NIEnumGateMode.

This enum maps the gate modes used by readers. It extends
EnumWrapper to provide conversion helpers between Python and Java enums.
"""
from enum import unique
from ndtkit_api.enum_wrapper import EnumWrapper


@unique
class NIEnumGateMode(EnumWrapper):
    """Enumerator of gate modes."""
    AMPLITUDE_MAXIMUM = "AMPLITUDE_MAXIMUM"
    FIRST_PEAK = "FIRST_PEAK"
    LAST_PEAK = "LAST_PEAK"
    ERROR = "ERROR"

    def get_java_enum_class_path(self) -> str:
        return "agi.ndtkit.api.model.readers.NIEnumGateMode"
