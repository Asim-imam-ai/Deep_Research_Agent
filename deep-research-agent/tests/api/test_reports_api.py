from uuid import uuid4


def test_missing_report(api):
    client, _ = api

    class EmptyReports:
        def get(self, db, report_id):
            return None

    # No DB access required for this mocked service.
    from unittest.mock import patch

    with patch(
        "research_assistant.api.v1.endpoints.reports.ReportManagementService",
        return_value=EmptyReports(),
    ):
        assert client.get(f"/api/v1/reports/{uuid4()}").status_code == 404
