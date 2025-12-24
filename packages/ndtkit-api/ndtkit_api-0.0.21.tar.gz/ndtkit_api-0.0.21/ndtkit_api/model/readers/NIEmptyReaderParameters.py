from .NIReaderParameters import NIReaderParameters
from ...ndtkit_socket_connection import gateway


class NIEmptyReaderParameters(NIReaderParameters):

    def __init__(self):
        super().__init__(gateway.jvm.agi.ndtkit.api.model.readers.NIEmptyReaderParameters())  # type: ignore
