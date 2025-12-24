from pydantic_ai_kernel import (
    PydanticAIBaseKernel,
)
from .tools import rudi_toolset


class RudiKernel(PydanticAIBaseKernel):
    """
    Kernel wrapper for pydantic agents.
    """

    implementation = "Rudi Agent"
    implementation_version = "1.0"
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "rudi",
        "mimetype": "text/plain",
        "file_extension": ".txt",
    }
    banner = "Rudi Agent"

    def __init__(self, **kwargs):
        super().__init__(kernel_name="rudi", toolsets=[rudi_toolset], **kwargs)
