from dataclasses import dataclass
from enum import StrEnum

from a2a.server.agent_execution import RequestContext


class Illocution(StrEnum):
    """Illocutions that are used in messages."""

    TELL = "tell"
    ACHIEVE = "achieve"
    ASK = "ask"
    PROPOSE = "propose"


@dataclass
class ACLMessage:
    illocution: Illocution
    content: str
    sender: str
    codec: str


@dataclass
class ACLIncomingMessage(ACLMessage):
    task_id: str
    origin: RequestContext
