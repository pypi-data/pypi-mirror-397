from ..NIReaderParameters import NIReaderParameters
from ....ndtkit_socket_connection import gateway
from ..NIEnumOverlapMethod import NIEnumOverlapMethod


class NIISQUSReaderParameters(NIReaderParameters):

    def __init__(self):
        super().__init__(gateway.jvm.agi.ndtkit.api.model.readers.isqus.NIISQUSReaderParameters())  # type: ignore

    def init_from_config_file(self, config_file: str) -> None:
        """Initialize ISQUS reader parameters from a configuration file.

        Args:
            config_file: Path to the ISQUS configuration file.
        """
        self._java_object.initFromConfigFile(config_file)

    def set_backlash(self, backlash: float) -> None:
        """Set the backlash value."""
        self._java_object.setBacklash(float(backlash))

    def set_overlap_ascan_selection(self, overlap: NIEnumOverlapMethod) -> None:
        """Set the overlap value."""
        self._java_object.setOverlapAscanSelection(overlap.to_java_enum())

    def set_replace_by_bwg_if_fg_is_noe(self, replace_by_bwg_if_fg_is_noe: bool) -> None:
        """Set the replace_by_bwg_if_fg_is_no_e value."""
        self._java_object.setReplaceByBWGIfFGisNoE(replace_by_bwg_if_fg_is_noe)

    def set_replace_by_bwg_if_fg_is_noe_overlap(self, overlap: NIEnumOverlapMethod) -> None:
        """Set the replace_by_bwg_if_fg_is_no_e_overlap value."""
        self._java_object.setReplaceByBWGIfFGisNoEOverlap(overlap.to_java_enum())

    def set_task_with_max_echo_in_bwg(self, task_with_max_echo_in_bwg: bool) -> None:
        """Set the task_with_max_echo_in_bwg value."""
        self._java_object.setTaskWithMaxEchoInBWG(task_with_max_echo_in_bwg)

    def set_add_bwg_in_alok(self, add_bwg_in_alok: bool) -> None:
        """Set the add_bwg_in_alok value."""
        self._java_object.setAddBWGInAlok(add_bwg_in_alok)
