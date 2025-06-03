# storage/json_file.py
import json
import os
from .base import StorageBase

class JSONFileStorage(StorageBase):
    def __init__(self, filepath="data.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    async def save(self, data: dict):
        # Simple async simulation — actual async file writing requires aiofiles or similar lib
        with open(self.filepath, "r+") as f:
            existing = json.load(f)
            existing.append(data)
            f.seek(0)
            json.dump(existing, f, indent=2)
