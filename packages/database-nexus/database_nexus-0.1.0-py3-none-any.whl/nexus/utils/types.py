#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

import json
import uuid
from typing import Any, Union
from pydantic import fields


class JSONType:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class UUIDType:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        elif isinstance(v, uuid.UUID):
            return v
        raise ValueError("Invalid UUID")