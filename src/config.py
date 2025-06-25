import json
import os
from typing import TypedDict, List, Dict, Any
import lib.definitions as d

class Params(TypedDict):
    STATEMENT_FOLDER: str
    VANCITY_PATH: str
    SUPPORTED_EXTENSIONS: list[str]
    DEBUG_MODE: bool
    LOANS: List[Dict[str, Any]]
    VANCITY_ACCOUNT_NUMBER: str
    REDACT_STATEMENTS: bool

# Load params.json from the project root
root_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(root_dir, "../params.json"), "r") as f:
    config: Params = json.load(f)
