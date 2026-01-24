from typing import Literal
from pydantic import BaseModel


class RoutingDecision(BaseModel):
    agent: Literal[
        "filesystem",
        "admin",
        "network",
        "networkandfile",
        "security",
        "usagemonitoring",
        "datetime"
    ]

    reason: str
    
