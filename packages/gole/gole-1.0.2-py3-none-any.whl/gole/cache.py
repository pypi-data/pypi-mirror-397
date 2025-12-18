from typing import Mapping

from aiopathlib import AsyncPath
from asynctinydb import TinyDB
from asynctinydb.table import Document, StrID, Table

from gole.config import settings

db = TinyDB(
    settings.cache_dir / 'cache.json', indent=4, separators=(',', ': ')
)


class PathID(StrID):
    def __init__(self, value: AsyncPath):
        self.value = value

    def __hash__(self):
        return hash(str(self.value))


class TextCache(Document[PathID]):
    def __init__(self, value: Mapping, doc_id: PathID | AsyncPath):
        super().__init__(value, PathID(doc_id))


class Cache:
    TEXT_CACHE: Table[PathID, TextCache] = db.table(
        'text_area', document_id_class=PathID, document_class=TextCache
    )
