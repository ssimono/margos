import asyncio
import logging

from threading import Thread, Event
from time import sleep as sync_sleep


async def call_program(cmd):
    proc = await asyncio.create_subprocess_exec(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    logging.info(f"Calling '{cmd}'")
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
    await asyncio.sleep(2)

    if proc.returncode != 0:
        return (cmd, f"Exited with code {proc.returncode}")
    else:
        return (cmd, stdout.decode("utf8"))


async def consumer(cmd, queue):
    cmd_result = await call_program(cmd)
    await queue.put(cmd_result)


async def _worker(router):
    q = asyncio.Queue()
    running = set()
    while len(router.schedules):
        for missing in router.schedules - running:
            asyncio.create_task(consumer(missing, q))
            running.add(missing)
        (schedule, result) = await q.get()
        running.remove(schedule)
        asyncio.get_event_loop().call_soon_threadsafe(router.render, schedule, result)


def worker(loop, router):
    logging.info("Worker started")
    asyncio.set_event_loop(loop)

    while not len(router.schedules):
        logging.debug("Waiting for the first applet")
        sync_sleep(1)

    loop.run_until_complete(_worker(router))
    logging.info("Worker ended")
