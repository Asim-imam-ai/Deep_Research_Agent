"""Report generation state for parallel report-writing nodes."""

from typing import NotRequired, TypedDict


class ReportState(TypedDict):
    """State used to generate and assemble the final research report."""

    topic: str

    # Each research section is stored as a JSON-compatible dictionary.
    sections: list[dict]

    # Independent report-writing nodes populate these keys.
    introduction: NotRequired[str]
    findings: NotRequired[str]
    conclusion: NotRequired[str]

    # The finalized report is also checkpoint-compatible.
    report: NotRequired[dict]
