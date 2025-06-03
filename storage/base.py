# storage/base.py

class StorageBase:
    async def save(self, data: dict):
        raise NotImplementedError("Save method must be implemented by subclasses")
