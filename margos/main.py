#! /usr/bin/env python3

import logging
from os import getenv
from asyncio import get_event_loop, get_child_watcher, Queue
from functools import partial
from threading import Thread

from margos.models import PanelEvent
from margos.display import render_loop
from margos.worker import safe_put, worker_thread

DEV = getenv("ENVIRONMENT", "prod") == "dev"
IID = "MargosDevApplet" if DEV else "MargosApplet"

logger = logging.getLogger("margos")


if __name__ == "__main__":
    log_level = logging.DEBUG if DEV else logging.INFO
    logging.basicConfig(
        level=log_level, format="[%(asctime)s] %(threadName)s - %(message)s"
    )

    # Make sure that child thread gets an event loop
    loop = get_event_loop()
    get_child_watcher().attach_loop(loop)

    applet_queue: "Queue[PanelEvent]" = Queue()

    worker = Thread(target=worker_thread, name="Worker", args=(loop, applet_queue))

    worker.start()
    render_loop(IID, partial(safe_put, loop, applet_queue))
    worker.join()
