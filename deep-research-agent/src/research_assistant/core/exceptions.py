"""Well-scoped errors surfaced by adapters and agents."""


class ResearchAssistantError(Exception):
    """Base domain/application exception."""


class ConfigurationError(ResearchAssistantError):
    """Required application configuration is missing or invalid."""


class SearchError(ResearchAssistantError):
    """Search adapter was unable to retrieve usable results."""


class AgentExecutionError(ResearchAssistantError):
    """Agent produced invalid output or could not proceed."""
