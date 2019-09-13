import random
from typing import List, Dict

from cloud_ui.components.model_view.model import Model

random_names = [f"name_{x}" for x in range(200)]


class ExampleModel(Model):
    TABLE_NAME = "example"

    def __init__(self):
        super().__init__()
        self.elements = dict()

    async def fetch_schema(self) -> List[dict]:
        return [
            dict(name='id', type=int),
            dict(name='name', type=str),
            dict(name='value', type=str),
            dict(name='count', type=int)
        ]

    async def get_count(self) -> int:
        self.logger.debug(f"E get_count")
        await self.fetch()
        self.logger.debug(f"L get_count")
        return len(self.ids)

    async def get_ids(self) -> List[int]:
        self.logger.debug(f"E get_ids")
        result = []
        for x in range(random.randint(80, 100)):
            result.append(x)
        self.logger.debug(f"L get_ids {result}")
        return result

    async def get_by_id(self, id) -> Dict:
        if id not in self.elements:
            element = dict(
                id=id,
                name=random_names[id],
                value=f"{random.choice(list('ABCDEFGHIJKLMNOPRQSTU'))}_{random.randint(2000, 5000)}",
                count=random.randint(50, 10000)
            )
            self.elements[id] = element
        return self.elements[id]