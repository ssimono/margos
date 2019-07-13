#! /usr/bin/env python3

import logging
import sys
from asyncio import get_event_loop, get_child_watcher, Queue
from functools import partial
from threading import Thread

from margos.system import conf, install, uninstall
from margos.models import PanelEvent
from margos.display import render_loop
from margos.worker import safe_put, worker_thread

logger = logging.getLogger("margos")


def main() -> None:
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "install":
            sys.exit(install())
        elif cmd == "uninstall":
            sys.exit(uninstall())

    log_level = logging.DEBUG if conf.env == "dev" else logging.INFO
    logging.basicConfig(
        level=log_level, format="[%(asctime)s] %(threadName)s - %(message)s"
    )

    # Make sure that child thread gets an event loop
    loop = get_event_loop()
    get_child_watcher().attach_loop(loop)

    applet_queue: "Queue[PanelEvent]" = Queue()

    worker = Thread(target=worker_thread, name="Worker", args=(loop, applet_queue))

    worker.start()
    render_loop(partial(safe_put, loop, applet_queue))
    worker.join()


if __name__ == "__main__":
    main()
