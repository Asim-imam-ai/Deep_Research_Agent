"""Tavily API adapter for external research search."""

import logging
from typing import Any

from tavily import TavilyClient as TavilySDKClient

from research_assistant.core.config import Settings, get_settings
from research_assistant.core.exceptions import ConfigurationError, SearchError

logger = logging.getLogger(__name__)


class TavilyClient:
    """Adapter between the Tavily SDK and the research application."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        tool: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.tool = tool

        if tool is None:
            api_key = self.settings.tavily_api_key.strip()

            if not api_key:
                raise ConfigurationError("TAVILY_API_KEY is required to search the web")

            self.client = TavilySDKClient(api_key=api_key)
        else:
            self.client = None

    def search(
        self,
        query: str,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Search Tavily and return results for normalization."""

        query = query.strip()

        if not query:
            raise ValueError("Search query must not be empty")

        try:
            if self.tool is not None:
                # Preserve support for existing injected test tools.
                result = self.tool.invoke({"query": query})
            else:
                result = self.client.search(
                    query=query,
                    search_depth="basic",
                    max_results=self.settings.tavily_max_results,
                )

        except Exception as exc:
            logger.exception(
                "Tavily request failed for query=%r",
                query,
            )
            raise SearchError("Tavily request failed") from exc

        if not isinstance(result, (dict, list)):
            raise SearchError("Tavily returned an unsupported response")

        items = result.get("results", []) if isinstance(result, dict) else result

        if not isinstance(items, list):
            raise SearchError("Tavily results must be a list")

        logger.info(
            "Tavily returned %d raw results for query=%r",
            len(items),
            query,
        )

        return result
