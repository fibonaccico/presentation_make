import uuid

from pydantic import BaseModel


class PresentationSchema(BaseModel):
    uuid: uuid.UUID
    status: str


class PaySchema(BaseModel):
    uuid: uuid.UUID
    paid_qty: int
