from pydantic import BaseModel
from typing import List
from datetime import time

class ListItem(BaseModel):
    fly_type_landing: str
    point_id: int
    time_create_action: time
    size_passenger: int

class Item(BaseModel):
    ids: List[int]
    time_start: List[time]
    time_end: time
    distance: List[int]
    tasks: List[ListItem]

Item(**{
    "ids": [0],
    "time_start": [time(0,0,0)],
    "time_end": time(0,0,0),
    "distance": [0],
    "tasks": [
        {
            "fly_type_landing": "d",
            "point_id": 1,
            "time_create_action": time(0,0,0),
            "size_passenger": 4
        }
    ]
})