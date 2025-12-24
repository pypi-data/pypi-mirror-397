"""Python wrapper for agi.ndtkit.api.model.readers.NIEnumOverlapMethod.

This enum maps the overlap methods used by readers. It extends
EnumWrapper to provide conversion helpers between Python and Java enums.
"""
from enum import unique
from ndtkit_api.enum_wrapper import EnumWrapper


@unique
class NIEnumOverlapMethod(EnumWrapper):
    """Overlap method to be used for reader."""
    MAXIMAL_VALUE = "MAXIMAL_VALUE"
    MINIMAL_VALUE = "MINIMAL_VALUE"
    MAXIMAL_AMPLITUDE_VALUE = "MAXIMAL_AMPLITUDE_VALUE"
    MINIMAL_AMPLITUDE_VALUE = "MINIMAL_AMPLITUDE_VALUE"
    MAXIMAL_TOF_VALUE = "MAXIMAL_TOF_VALUE"
    MINIMAL_TOF_VALUE = "MINIMAL_TOF_VALUE"
    FIRST_VALUE = "FIRST_VALUE"
    LAST_VALUE = "LAST_VALUE"

    def get_java_enum_class_path(self) -> str:
        return "agi.ndtkit.api.model.readers.NIEnumOverlapMethod"
