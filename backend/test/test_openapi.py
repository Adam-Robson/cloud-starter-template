import json

import pytest

from backend.services import export_openapi


def test_exports_camel_case_schema(capsys: pytest.CaptureFixture[str]) -> None:
    export_openapi()
    schema = json.loads(capsys.readouterr().out)
    item = schema['components']['schemas']['Item']['properties']
    assert 'createdAt' in item


def test_documents_error_response(capsys: pytest.CaptureFixture[str]) -> None:
    export_openapi()
    schema = json.loads(capsys.readouterr().out)
    responses = schema['paths']['/api/items']['post']['responses']
    assert responses['default']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/ErrorResponse'
    }
    assert 'HTTPValidationError' not in schema['components']['schemas']
