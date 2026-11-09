import pytest
from pydantic import ValidationError

from backend.lib.models import ApiModel, ErrorResponse, Page


class Widget(ApiModel):
    widget_id: str
    display_name: str


def test_dumps_camel_case() -> None:
    widget = Widget(widget_id='w1', display_name='Gear')
    assert widget.model_dump() == {'widgetId': 'w1', 'displayName': 'Gear'}


def test_accepts_snake_and_camel_input() -> None:
    from_camel = Widget.model_validate(
        {'widgetId': 'w1', 'displayName': 'Gear'}
    )
    from_snake = Widget.model_validate(
        {'widget_id': 'w1', 'display_name': 'Gear'}
    )
    assert from_camel == from_snake


def test_ignores_unknown_fields() -> None:
    widget = Widget.model_validate(
        {'widgetId': 'w1', 'displayName': 'Gear', 'extra': True}
    )
    assert not hasattr(widget, 'extra')


def test_is_immutable() -> None:
    widget = Widget(widget_id='w1', display_name='Gear')
    with pytest.raises(ValidationError):
        widget.display_name = 'Cog'


def test_error_response_shape() -> None:
    error = ErrorResponse(status_code=404, message='Not found')
    assert error.model_dump() == {
        'statusCode': 404,
        'message': 'Not found',
        'detail': None,
    }


@pytest.mark.parametrize(
    ('page', 'total', 'expected'),
    [(1, 25, True), (3, 25, False), (1, 10, False)],
)
def test_page_has_next(page: int, total: int, expected: bool) -> None:
    result = Page[Widget](items=[], total=total, page=page, page_size=10)
    assert result.has_next is expected


def test_page_parses_nested_items() -> None:
    result = Page[Widget].model_validate(
        {
            'items': [{'widgetId': 'w1', 'displayName': 'Gear'}],
            'total': 1,
            'pageSize': 10,
        }
    )
    assert result.items == [Widget(widget_id='w1', display_name='Gear')]
