"""Framework integrations for Protectron SDK."""

from protectron.integrations.base import BaseIntegration

__all__ = ["BaseIntegration"]

# Lazy imports for optional dependencies
def __getattr__(name: str):
    if name == "ProtectronCallbackHandler":
        from protectron.integrations.langchain import ProtectronCallbackHandler
        return ProtectronCallbackHandler
    elif name == "ProtectronCrewAI":
        from protectron.integrations.crewai import ProtectronCrewAI
        return ProtectronCrewAI
    elif name == "with_protectron":
        from protectron.integrations.crewai import with_protectron
        return with_protectron
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
