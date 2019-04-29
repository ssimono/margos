#! /usr/bin/env python3

import logging
import asyncio
from os import getenv
from threading import Thread

from display import render_loop, Router
from worker import worker

DEV = getenv("ENVIRONMENT", "prod") == "dev"
IID = "MargosDevApplet" if DEV else "MargosApplet"


logger = logging.getLogger("margos")

if __name__ == "__main__":
    log_level = logging.DEBUG if DEV else logging.INFO
    logging.basicConfig(
        level=log_level, format="[%(asctime)s] %(threadName)s - %(message)s"
    )

    # Make sure that child thread gets an event loop
    asyncio.get_child_watcher().attach_loop(asyncio.get_event_loop())

    router = Router()
    worker_thread = Thread(
        target=worker, name="Worker", args=(asyncio.get_event_loop(), router)
    )

    worker_thread.start()
    render_loop(IID, router)
    worker_thread.join()
