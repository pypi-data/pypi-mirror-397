from importlib.metadata import version
from .metadata_model import MetadataRecord
from .uploader_radboudfdp import RadboudFDPClient

# __version__ = version("fairmeta")

__all__ = (
    "MetadataRecord",
    "gatherers",
    "RadboudFDPClient"
)

def __dir__() -> "list[str]":
    return list(__all__)