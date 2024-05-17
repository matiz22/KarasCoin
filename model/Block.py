from pydantic import BaseModel
from typing import List


class Block(BaseModel):
    index: int
    timestamp: float
    transactions: List[str]
    proof: int
    previous_hash: str
