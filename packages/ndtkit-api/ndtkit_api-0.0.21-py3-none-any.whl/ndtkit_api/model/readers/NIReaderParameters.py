"""Python wrapper for agi.ndtkit.api.model.readers.NIReaderParameters.

This module provides a thin Python wrapper around the Java NIReaderParameters
class, exposing its methods in a Pythonic way. It delegates calls to the
underlying Java object and handles enum conversions where necessary.
"""
from py4j.java_gateway import JavaObject
from .NIEnumAmplitudeSign import NIEnumAmplitudeSign
from .NIEnumGateMode import NIEnumGateMode
from .NIEnumOverlapMethod import NIEnumOverlapMethod


class NIReaderParameters:
    """Wrapper for agi.ndtkit.api.model.readers.NIReaderParameters."""

    def __init__(self, java_object: JavaObject):
        self._java_object = java_object

    def set_gate_parameters(
        self,
        gate_start: float,
        gate_end: float,
        threshold: float,
        sign: NIEnumAmplitudeSign,
        ascan_choose_mode: NIEnumGateMode,
    ) -> None:
        """Set gate parameters.

        Args:
            gate_start: Gate start in µs.
            gate_end: Gate end in µs.
            threshold: Threshold in %.
            sign: NIEnumAmplitudeSign (wrapper or Java enum).
            ascan_choose_mode: NIEnumGateMode (wrapper or Java enum).
        """
        self._java_object.setGateParameters(gate_start, gate_end, threshold, sign.to_java_enum(), ascan_choose_mode.to_java_enum())

    def set_overlap(self, overlap: NIEnumOverlapMethod) -> None:
        """Define Entry gate or Back Wall Gate overlap.

        Args:
            overlap: NIEnumOverlapMethod (wrapper or Java enum).
        """
        self._java_object.setOverlap(overlap.to_java_enum())

    def set_fg_overlap(self, overlap: NIEnumOverlapMethod) -> None:
        """Define Flaw gate overlap.

        Args:
            overlap: NIEnumOverlapMethod (wrapper or Java enum).
        """
        self._java_object.setFGOverlap(overlap.to_java_enum())
