from enum import Enum

QURAITE_ADAPTER_TRACE_PREFIX = "quraite-adapter"

QURAITE_TRACER_NAME = "quraite.instrumentation"


class Framework(str, Enum):
    """Supported agent frameworks."""

    PYDANTIC = "pydantic"
    LANGGRAPH = "langgraph"
    GOOGLE_ADK = "google_adk"
    OPENAI_AGENTS = "openai_agents"
    AGNO = "agno"
    SMOLAGENTS = "smolagents"
