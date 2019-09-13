import logging
from abc import abstractmethod
from typing import List, Dict
from remi import gui as G


class Model(object):
    PK = 'id'
    ITEMS_PER_PAGE = 10
    TABLE_NAME = "undefined"

    def __init__(self):
        self._ids = set()
        self._dirty = set()
        self.logger = logging.getLogger(f"{self}")

    def __str__(self):
        return f"<Model:{self.TABLE_NAME}>"

    @property
    def ids(self) -> list:
        return list(self._ids)

    @ids.setter
    def ids(self, values):
        self.logger.debug(f"setting new ids ... {values}")
        self._ids = set(values)

    async def fetch(self) -> bool:
        try:
            ids = await self.get_ids()
            self.logger.debug(f"IDS = {ids}")
            self.ids = ids
            return True
        except Exception as e:
            return False

    @abstractmethod
    async def fetch_schema(self) -> List[Dict]:
        """

        :return: [dict(name=field1_name, type=field1_type), ...]
        """

    async def sync(self):
        self._dirty = set()

    @abstractmethod
    async def get_count(self) -> int:
        """
        returns data amount size
        :return: int
        """

    @abstractmethod
    async def get_ids(self) -> List[int]:
        """
        returns all elements ids
        :return:
        """

    @abstractmethod
    async def get_by_id(self, id) -> Dict:
        """
        returns element by id
        :param id:
        :return:
        """

