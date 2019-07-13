import asyncio
import logging

from asyncio import Queue, CancelledError, ensure_future

from margos.models import (
    AppletAdded,
    AppletRemoved,
    ConfigUpdated,
    FactoryDown,
    PanelEvent,
    AppletConfig,
    Renderer,
)

from margos.parsing import parse

_Loop = asyncio.AbstractEventLoop

# Use Python3.7 naming
create_task = ensure_future


async def _call_program(command: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    logging.info(f"Calling '{command}'")
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)

    if proc.returncode != 0:
        return f"Exited with code {proc.returncode}"
    return stdout.decode("utf8")


async def _command_interval(config: AppletConfig, callback: Renderer) -> Renderer:
    try:
        while True:
            call_result = await _call_program(config.command)
            await asyncio.sleep(config.interval)
            callback(parse(call_result))
    except CancelledError:
        return callback


async def schedule(applet_queue: "Queue[PanelEvent]") -> None:
    """ Listen to PanelEvents and schedule shell commands to run at interval """
    tasks = {}
    while True:
        event: PanelEvent = await applet_queue.get()
        if isinstance(event, AppletAdded):
            logging.info(f"Applet added: {event.id_}")
            tasks[event.id_] = create_task(
                _command_interval(event.config, event.render)
            )
        elif isinstance(event, AppletRemoved):
            logging.info(f"Applet removed: {event.id_}")
            tasks[event.id_].cancel()
        elif isinstance(event, ConfigUpdated):
            logging.info(f"Applet updated: {event.id_}")
            tasks[event.id_].cancel()
            render = await tasks[event.id_]
            tasks[event.id_] = create_task(_command_interval(event.config, render))
        elif isinstance(event, FactoryDown):
            break


def safe_put(loop: _Loop, queue: "asyncio.Queue[PanelEvent]", e: PanelEvent) -> None:
    async def _put(e: PanelEvent) -> None:
        return await queue.put(e)

    asyncio.run_coroutine_threadsafe(_put(e), loop)


def worker_thread(loop: _Loop, applet_queue: "asyncio.Queue[PanelEvent]") -> None:
    logging.info("Worker started")
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule(applet_queue))
    logging.info("Worker ended")
