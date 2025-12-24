from a2a.server.events import EventQueue

from a2a_acl.agent.acl_agent import ACLAgentExecutor
from a2a_acl.content_codecs.common import natural_language_id

from a2a_acl.protocol.acl_message import ACLMessage, Illocution
from a2a_acl.a2a_utils.send_message import sync_reply

from a2a_acl.interface import asi_parser
from a2a_acl.interface.interface import ACLAgentCard


my_card = asi_parser.read_file("validator.asi").add_codecs([natural_language_id])


def ask_validation(ref: str, t: str):
    print("Reference: " + ref)
    print("Proposal: " + t)
    print("Do you validate this proposal ?")
    res = input("[Y/N/Q]\n")
    match res:
        case "Y" | "y":
            print("Validated. (" + res + ")")
            return "valid"
        case "Q" | "q":
            print("Quit. (" + res + ")")
            return "quit"
        case _:
            print("Not Validated. (" + res + ")")
            return "invalid"


class ValidatorAgentExecutor(ACLAgentExecutor):

    def __init__(self, card: ACLAgentCard, url):
        super().__init__(agentcard=card, my_url=url)
        print(
            "Warning: launching a pure python A2A agent, unable to check .asi interface against python body."
        )
        self.add_message_handler(Illocution.PROPOSE, self.execute_propose)
        self.reference = ""

    async def execute_achieve(
        self,
        m: ACLMessage,
        output_event_queue: EventQueue,
    ):
        pass

    async def execute_tell(
        self,
        m: ACLMessage,
        output_event_queue: EventQueue,
    ):
        self.reference = m.content
        await sync_reply(output_event_queue, "ack")
        print("Received an update of the reference.")

    async def execute_ask(
        self,
        m: ACLMessage,
        output_event_queue: EventQueue,
    ):
        pass

    async def execute_propose(
        self,
        m: ACLMessage,
        output_event_queue: EventQueue,
    ):
        res = ask_validation(self.reference, m.content)
        await sync_reply(output_event_queue, res)
        return
