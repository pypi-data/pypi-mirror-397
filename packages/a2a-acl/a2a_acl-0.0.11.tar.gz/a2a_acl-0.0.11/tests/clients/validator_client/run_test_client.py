import time

import a2a

import context

from a2a.types import (
    AgentCard,
    TaskStatusUpdateEvent,
)

from a2a_acl.protocol.send_acl_message import (
    send_acl_message,
    spawn_send_acl_message,
    extract_text_from_task,
    extract_text_from_message,
)
from a2a_acl.a2a_utils.card_holder import download_card


from a2a_acl.utils.url import build_url

host = "127.0.0.1"


def handle_status_update(e, t):
    match type(t):
        case a2a.types.TaskStatusUpdateEvent:
            print("(status update: " + str(t.status.state) + ")")
        case _:
            print("(status update ignored)")


async def main() -> None:
    target_agent_url = build_url(host, context.port_validator)

    # Fetch Public Agent Card and Initialize Client
    target_agent_card: AgentCard | None = None

    try:
        target_agent_card = await download_card(target_agent_url)

    except Exception:
        print("Client failed to fetch the public agent card. Cannot continue.")
        exit(-1)

    spawn_send_acl_message(
        target_agent_card,
        "tell",
        "A function to reverse the order of the elements of a list.",
        "",
        "nl",
        message_processor=(
            lambda m: print("Message event: " + extract_text_from_message(m))
        ),
        task_processor=(
            lambda t: print("Task artifact event: " + extract_text_from_task(t))
        ),
        status_update_processor=handle_status_update,
    )
    print("[Tell-Message sent to validator agent.]")

    await asyncio.sleep(0.5)

    spawn_send_acl_message(
        target_agent_card,
        "propose",
        "The function should return an integer.",
        "",
        "nl",
        message_processor=(lambda m: print("Message: " + str(m))),
        task_processor=(lambda t: print("Task artifact: " + extract_text_from_task(t))),
        status_update_processor=handle_status_update,
    )
    print("[Propose-Message sent to validator agent.]")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
    input("Press Enter to exit.\n")
