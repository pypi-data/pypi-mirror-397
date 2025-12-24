import asyncio
import uuid
from threading import Thread

import a2a
import httpx
from a2a.client import ClientFactory, ClientConfig
from a2a.types import (
    AgentCard,
    PushNotificationConfig,
    Message,
    Role,
    TextPart,
    Task,
)

from a2a_acl.a2a_utils.card_holder import download_card


def extract_text_from_message(m: Message) -> str:
    return m.parts[0].root.text


def extract_text_from_task(t: Task) -> str:
    res = ""
    if t.artifacts:
        a = t.artifacts[-1]
        for p in a.parts:
            if p.root.kind == "text":
                res = res + p.root.text
        return res
    else:
        return ""


def default_message_handler(m: Message) -> None:
    print("(Message event received: " + extract_text_from_message(m) + ")")


def default_task_handler(t: Task) -> None:
    print("(Task event received: " + extract_text_from_task(t) + ")")


def default_status_update_handler(e, t) -> None:
    print("(Status update event received: " + str(type(t)) + ")")


class SendFailureException(Exception):
    pass


# derived from https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/number_guessing_game/utils/protocol_wrappers.py
async def send_acl_message(
    target: AgentCard | str,
    illocution: str,
    text: str,
    my_url: str,
    codec: str,
    message_processor=default_message_handler,
    task_processor=default_task_handler,
    status_update_processor=default_status_update_handler,
):
    """Send *text* to the target agent via the A2A ``message/send`` operation.

    Args:
        target: card or url of the target agent.
        illocution : illocution such as 'tell' or 'achieve'
        text: Payload to send as a plain-text message.
        my_url: the url of sender's server for replies.
        codec: the codec used to code the content of the message.
        message_processor: the processor used to process the 'message' text parts.
        task_processor: the processor used to process the 'task' text parts.
        status_update_processor : the processor used to process the 'status' updates.

    Returns:
        Nothing.
    """
    if isinstance(target, str):
        try:
            target = await download_card(target)
        except Exception:
            print("Error: Cannot get agent card. Send failed.")
            raise SendFailureException

    assert isinstance(target, AgentCard)

    _client_factory = ClientFactory(
        ClientConfig(
            push_notification_configs=[PushNotificationConfig(url=my_url)],
            httpx_client=httpx.AsyncClient(timeout=httpx.Timeout(timeout=30)),
            streaming=target.capabilities.streaming,
        )
    )
    client = _client_factory.create(target)
    md: dict[str, str] = {"illocution": illocution, "codec": codec}
    msg = Message(
        kind="message",
        role=Role.agent,
        message_id=uuid.uuid4().hex,
        parts=[TextPart(text=text, metadata=md)],
        metadata=md,
    )

    last_message = None

    def dispatch(e, m_handler, t_handler):
        match type(e):
            case a2a.types.Message:
                m_handler(e)
            case a2a.types.Task:
                t_handler(event)
            case _:
                print("Event not supported: " + str(type(event)))

    try:
        # Warning : concurrent async generators work badly in python
        # -> two concurrent message sending should be in two separate threads
        # (see spawn_send_message below)
        async for event in client.send_message(msg):
            # Unwrap tuple from transport implementations
            if isinstance(event, tuple):
                (event, other) = event
                if other is not None:
                    match type(other):
                        case a2a.types.TaskStatusUpdateEvent:
                            status_update_processor(event, other)
                        case a2a.types.TaskArtifactUpdateEvent:
                            dispatch(event, message_processor, task_processor)
                        case _:
                            print("(Additional " + str(type(other)) + " received.)")
                else:
                    dispatch(event, message_processor, task_processor)
            else:
                dispatch(event, message_processor, task_processor)

    except a2a.client.errors.A2AClientTimeoutError:
        print(
            "Warning: no synchronous reply before timeout. Some information might be lost."
        )
    except Exception:
        print("Send failed.")
        raise SendFailureException


# hard reference to task that must not be garbage collected.
launched_tasks = []
# Note that if we never delete tasks from this list, we create a memory leak.


class SendMessageThread(Thread):
    def __init__(
        self,
        dest: AgentCard | str,
        illocution: str,
        content: str,
        sender: str,
        codec: str,
        message_processor=default_message_handler,
        task_processor=default_task_handler,
        status_update_processor=default_status_update_handler,
    ):
        super().__init__()
        self.dest = dest
        self.illocution = illocution
        self.content = content
        self.reply_to = sender
        self.codec = codec
        self.message_processor = message_processor
        self.task_processor = task_processor
        self.status_update_processor = status_update_processor

    def run(self):
        loop = asyncio.new_event_loop()
        t = loop.create_task(
            send_acl_message(
                self.dest,
                self.illocution,
                self.content,
                self.reply_to,
                self.codec,
                self.message_processor,
                self.task_processor,
                self.status_update_processor,
            )
        )
        launched_tasks.append(t)
        loop.run_until_complete(t)


def spawn_send_acl_message(
    dest: AgentCard | str,
    illocution: str,
    content: str,
    sender: str,
    codec: str,
    message_processor=default_message_handler,
    task_processor=default_task_handler,
    status_update_processor=default_status_update_handler,
) -> None:
    t = SendMessageThread(
        dest,
        illocution,
        content,
        sender,
        codec,
        message_processor,
        task_processor,
        status_update_processor,
    )
    t.start()
