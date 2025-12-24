import time

import context
from a2a_acl.agent.server_utils import run_server
from validator import (
    ValidatorAgentExecutor,
)
from a2a_acl.utils.url import build_url


the_host = "127.0.0.1"
my_url = build_url(the_host, context.validator_port)


async def main() -> None:
    run_server(
        ValidatorAgentExecutor(build_url(the_host, context.validator_port)),
        the_host,
        context.validator_port,
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

    while True:
        time.sleep(1)
