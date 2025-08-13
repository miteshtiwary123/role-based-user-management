from pydantic import BaseModel
from typing import Generic, List, TypeVar

T = TypeVar("T")

class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int

class Paginated(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta
    