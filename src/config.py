import json
import os
from typing import TypedDict

class Params(TypedDict):
    STATEMENT_FOLDER: str
    SUPPORTED_EXTENSIONS: list[str]
    DEBUG_MODE: bool

# Load params.json from the project root
root_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(root_dir, "params.json"), "r") as f:
    config: Params = json.load(f)
