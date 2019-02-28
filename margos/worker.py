import asyncio
import logging

from threading import Thread, Event


async def call_program(render_bus):
    cmd = "date"
    proc = await asyncio.create_subprocess_exec(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    logging.info(f"Calling '{cmd}'")
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
    if proc.returncode != 0:
        logging.info(f"[program exited with {proc.returncode}]")
    else:
        render_bus.emit("margos_render", stdout.decode("utf8"))


async def worker(render_bus, drain_flag):
    while not drain_flag.is_set():
        task = asyncio.create_task(call_program(render_bus))
        await asyncio.sleep(2)
        await task


class WorkerThread(Thread):
    def __init__(self, loop, render_bus):
        # Cannot pass extra args if I override run, so using another method
        super().__init__(target=self.entrypoint, args=(loop, render_bus))

        self.drain_flag = Event()

    def entrypoint(self, loop, render_bus):
        logging.info("Runner started")
        asyncio.set_event_loop(loop)
        loop.run_until_complete(worker(render_bus, self.drain_flag))
        logging.info("Runner ended")

    def drain(self):
        self.drain_flag.set()
