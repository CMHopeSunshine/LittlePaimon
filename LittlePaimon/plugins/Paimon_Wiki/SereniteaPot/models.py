from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    num: int
    wiki_url: Optional[str] = None
    level: int
    icon_url: str
