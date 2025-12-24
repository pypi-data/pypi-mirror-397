"""Python wrapper for agi.ndtkit.api.model.readers.NIEnumAmplitudeSign.

This enum maps the amplitude signs used by readers. It extends
EnumWrapper to provide conversion helpers between Python and Java enums.
"""
from enum import unique
from ndtkit_api.enum_wrapper import EnumWrapper


@unique
class NIEnumAmplitudeSign(EnumWrapper):
    """Enumerator of amplitude sign."""
    ABSOLUTE = "ABSOLUTE"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"

    def get_java_enum_class_path(self) -> str:
        return "agi.ndtkit.api.model.readers.NIEnumAmplitudeSign"
