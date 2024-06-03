from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from .member import Member  # Importing Member class from another file

@dataclass
class Vote:
    id: int
    date: datetime
    description: str
    result: str
    member_votes: List['MemberVote']

@dataclass
class MemberVote:
    member_id: int
    vote: str
