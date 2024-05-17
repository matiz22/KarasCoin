from pydantic import BaseModel


class Transaction(BaseModel):
    angler: str
    fishery: str
    fish: str
    weight: float
