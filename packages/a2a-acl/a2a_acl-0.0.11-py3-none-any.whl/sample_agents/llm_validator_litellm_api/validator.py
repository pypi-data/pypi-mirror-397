import asyncio

from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Part, TextPart
from a2a.utils import new_task, new_agent_text_message

from a2a_acl.agent.acl_agent import ACLAgentExecutor
from a2a_acl.content_codecs.common import natural_language_id

from a2a_acl.protocol.acl_message import ACLMessage, Illocution, ACLIncomingMessage
from a2a_acl.a2a_utils.send_message import sync_reply

from a2a_acl.interface import asi_parser


from sample_agents.llm_validator_litellm_api.prompts import ask_llm_for_correctness

my_card = asi_parser.read_file("validator.asi").add_codecs([natural_language_id])


class ValidatorAgentExecutor(ACLAgentExecutor):

    def __init__(self, url):
        super().__init__(agentcard=my_card, my_url=url)
        print(
            "Warning: launching a pure python A2A agent,"
            " unable to check .asi interface against python body."
        )
        self.add_message_handler(Illocution.PROPOSE, self.execute_propose)
        self.spec = "A function to compare reverse the order of the elements in a list."

    async def execute_achieve(
        self,
        m: ACLMessage,
        output_event_queue: EventQueue,
    ):
        pass

    async def execute_tell(
        self,
        m: ACLIncomingMessage,
        output_event_queue: EventQueue,
    ):
        self.spec = m.content
        await sync_reply(output_event_queue, "ack")
        print("Received a new specification to consider.")

    async def execute_ask(
        self,
        m: ACLIncomingMessage,
        output_event_queue: EventQueue,
    ):
        pass

    async def execute_propose(
        self,
        m: ACLIncomingMessage,
        output_event_queue: EventQueue,
    ):

        print("(creating a new task)")
        task = new_task(m.origin.message)
        await output_event_queue.enqueue_event(task)
        updater = TaskUpdater(output_event_queue, task.id, task.context_id)

        await asyncio.sleep(1)

        await updater.update_status(
            TaskState.working,
            new_agent_text_message("start working", context_id=m.origin.context_id),
        )

        await asyncio.sleep(1)

        print("(consult llm)")
        res = ask_llm_for_correctness(
            self.spec,
            m.content,
        )
        await updater.update_status(
            TaskState.working,
            new_agent_text_message("finished working", context_id=m.origin.context_id),
        )

        await asyncio.sleep(1)

        atom = "valid" if res else "invalid"
        await updater.add_artifact(
            [Part(root=TextPart(text=str(atom)))], name="Final response."
        )

        await asyncio.sleep(1)

        await updater.complete()

        await asyncio.sleep(1)

        return
