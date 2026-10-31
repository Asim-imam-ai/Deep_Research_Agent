"""LangChain usage accounting. Price estimation requires a maintained model price catalog."""

from threading import Lock

from langchain_core.callbacks import BaseCallbackHandler

from research_assistant.observability.metrics import increment


class UsageCallback(BaseCallbackHandler):
    def __init__(self):
        self.lock = Lock()
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response, **kwargs):
        for generation in response.generations:
            for item in generation:
                message = getattr(item, "message", None)
                usage = getattr(message, "usage_metadata", None) or {}
                with self.lock:
                    self.input_tokens += int(usage.get("input_tokens", 0))
                    self.output_tokens += int(usage.get("output_tokens", 0))
        increment("llm.responses")

    def totals(self):
        with self.lock:
            return {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens}
