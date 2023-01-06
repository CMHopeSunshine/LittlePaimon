from typing import List, Optional

from pydantic import BaseModel, validator


class Member(BaseModel):
    star: int
    avatar: str
    name: str


class TeamRate(BaseModel):
    rate: float
    formation: List[Member]
    ownerNum: Optional[int]

    @validator('rate', pre=True)
    def str2float(cls, v):
        return float(v.replace('%', '')) / 100.0 if isinstance(v, str) else v


class TeamRateResult(BaseModel):
    rateListUp: List[TeamRate]
    rateListDown: List[TeamRate]
    userCount: int

    def sort_by_own(self, characters: List[str]):
        for team in self.rateListUp:
            team.ownerNum = len(set(characters) & {member.name for member in team.formation})
        for team in self.rateListDown:
            team.ownerNum = len(set(characters) & {member.name for member in team.formation})
        self.rateListUp.sort(key=lambda x: (x.ownerNum / 4 * x.rate), reverse=True)
        self.rateListDown.sort(key=lambda x: (x.ownerNum / 4 * x.rate), reverse=True)
