from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    '''Base for every shape sent or received over HTTP.

    Fields are snake_case in Python and camelCase on the wire, so payloads
    match TypeScript conventions on the frontend. Unknown fields from
    upstream services are ignored rather than rejected.
    '''

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        extra='ignore',
        frozen=True,
    )
