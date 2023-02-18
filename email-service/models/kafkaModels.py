from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EmailAlert(BaseModel):
    recipients: list[str]
    subject: str
    message: str
