'''Optional per-request settings accepted by the HTTP client.'''

from collections.abc import Mapping
from typing import Any, TypedDict

import httpx

from backend.lib.models import ApiModel


class RequestOptions(TypedDict, total=False):
    '''Optional per-request settings accepted by every client method.'''

    json: ApiModel
    params: httpx.QueryParams | Mapping[str, Any]
    headers: Mapping[str, str]
