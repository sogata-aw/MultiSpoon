import json

from pydantic import BaseModel
from typing import Optional

class LoggerData(BaseModel):
    level: str
    format: str

def load_commands():
    with open("./data/commands.json", "r") as json_data:
        return json.load(json_data)
