#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

from typing import Any, Optional
from pydantic import Field as PydanticField


def field(
        default: Any = ...,
        *,
        primary_key: bool = False,
        nullable: bool = True,
        unique: bool = False,
        index: bool = False,
        generated: bool = False,
        foreign_key: Optional[str] = None,
        **kwargs
):

    json_schema_extra = kwargs.pop('json_schema_extra', {})
    json_schema_extra.update({
        'primary_key': primary_key,
        'nullable': nullable,
        'unique': unique,
        'index': index,
        'generated': generated,
        'foreign_key': foreign_key
    })

    return PydanticField(
        default=default,
        json_schema_extra=json_schema_extra,
        **kwargs
    )