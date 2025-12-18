import argparse


import asyncio
from typing import Iterable
from smcore import hardcore
from smcore import agent


async def replay_agent(
    name: str,
    src_bb_addr: str,
    dest_bb_addr: str,
    tags: Iterable[str],
    ignore=False,
):
    src_bb = hardcore.HTTPTransit(src_bb_addr)
    dest_bb = hardcore.HTTPTransit(dest_bb_addr)

    dest_bb.set_name(name)

    src_agt = agent.Agent(src_bb)
    dest_agt = agent.Agent(dest_bb)

    if ignore:
        await src_agt.ignore_history()

    incoming_data = await src_agt.listen_for(tags)

    src_agt.start()
    print(f"replay from {src_bb_addr} -> {dest_bb_addr} on tags {tags}")
    while True:
        io_post = await incoming_data.get()
        print(f"replaying post from {src_bb_addr} -> {dest_bb_addr}")

        d = await io_post.data()
        md = await io_post.metadata()

        await dest_agt.post(md, d, io_post.tags())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(prog="smcore.replay")
    ap.add_argument(
        "--from",
        default="localhost:8080",
        help="set the source blackboard",
    )

    ap.add_argument(
        "--to",
        default="localhost:8080",
        help="set the destination blackboard",
    )

    ap.add_argument(
        "--name",
        default="replay-agent",
        help="set the replay agent name",
    )

    ap.add_argument(
        "--ignore", action="store_true", help="ignore existing blackboard messages"
    )

    ap.add_argument("--tags", action="extend", nargs="+", type=str)

    args = ap.parse_args()
    args = vars(args)

    asyncio.run(
        replay_agent(
            args["name"], args["from"], args["to"], args["tags"], ignore=args["ignore"]
        )
    )
