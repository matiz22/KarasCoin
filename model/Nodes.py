from typing import List

from pydantic import BaseModel


class Nodes(BaseModel):
    nodes: List[str]
