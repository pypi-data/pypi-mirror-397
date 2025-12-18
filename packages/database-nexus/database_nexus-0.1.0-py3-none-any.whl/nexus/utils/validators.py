#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

import re
from typing import Any
from pydantic import validator

def email_validator(v: str) -> str:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, v):
        raise ValueError("Invalid email format")
    return v

def phone_validator(v: str) -> str:
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, v):
        raise ValueError("Invalid phone number format")
    return v