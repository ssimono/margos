import asyncio
import logging

from threading import Thread, Event


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


async def scheduler(render_bus, drain_flag):
    # FIXME annoying that we need to wait for the first one
    # Maybe wait before starting the scheduler with an Event flag
    while len(render_bus.commands) == 0:
        await asyncio.sleep(2)

    q = asyncio.Queue()
    running = set()
    while not drain_flag.is_set():
        for missing in render_bus.commands - running:
            asyncio.create_task(consumer(missing, q))
            running.add(missing)
        (cmd, result) = await q.get()
        running.remove(cmd)
        asyncio.get_event_loop().call_soon_threadsafe(
            render_bus.emit, "margos_render", cmd, result
        )


class WorkerThread(Thread):
    def __init__(self, loop, render_bus):
        # Cannot pass extra args if I override run, so using another method as target
        super().__init__(target=self.entrypoint, args=(loop, render_bus))

        self.drain_flag = Event()

    def entrypoint(self, loop, render_bus):
        logging.info("Runner started")
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scheduler(render_bus, self.drain_flag))
        logging.info("Runner ended")

    def drain(self):
        self.drain_flag.set()
