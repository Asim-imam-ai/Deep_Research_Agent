from research_assistant.guardrails.source_validation import (
    unique_valid_sources,
    validate_source_url,
)


def test_reject_private_targets():
    for url in [
        "http://127.0.0.1/private",
        "http://localhost/admin",
        "file:///etc/passwd",
        "http://10.1.2.3",
    ]:
        assert not validate_source_url(url)


def test_deduplicate_public_urls():
    assert unique_valid_sources(
        ["https://example.com/", "https://example.com", "https://example.org"]
    ) == ["https://example.com/", "https://example.org"]
