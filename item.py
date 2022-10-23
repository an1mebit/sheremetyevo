from pydantic import BaseModel
from typing import List
from datetime import time
from analytic import *

class ListItem(BaseModel):
    id: int
    path: List[int]
    time_start: time
    time_end: time

class Item(BaseModel):
    __root__: List[ListItem]