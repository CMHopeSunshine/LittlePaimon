from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    num: int
    wiki_url: Optional[str]
    level: int
    icon_url: str
