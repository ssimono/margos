#! /usr/bin/env python3

import gi
import logging

import asyncio
import threading

gi.require_version("MatePanelApplet", "4.0")

from gi.repository import MatePanelApplet
from gi.repository import Gtk
from gi.repository import GObject

from worker import WorkerThread


def onclick(widget):
    logging.info("Clicked")


class MargosButton(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sender_listener = None

    def on_render(self, sender, value):
        self.set_label(value)


def applet_fill(applet, sender):
    button = MargosButton(label="Hello")
    button.connect("clicked", onclick)
    button.connect("destroy", sender.on_button_destroy)
    button.sender_listener = sender.connect("margos_render", button.on_render)
    applet.add(button)

    applet.show_all()
    logging.info("Applet created {}".format(applet))


def applet_factory(applet, iid, sender):
    if iid != "MargosApplet":
        return False

    applet_fill(applet, sender)
    return True


class Sender(GObject.GObject):
    def on_button_destroy(self, margos_button):
        logging.info("Destroying the button")
        logging.info(margos_button.sender_listener)
        self.disconnect(margos_button.sender_listener)


GObject.type_register(Sender)
GObject.signal_new(
    "margos_render",
    Sender,
    GObject.SignalFlags.RUN_FIRST,
    GObject.TYPE_NONE,
    (GObject.TYPE_GSTRING,),
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

    # Make sure that child thread gets an event loop
    asyncio.get_child_watcher().attach_loop(asyncio.get_event_loop())

    sender = Sender()
    worker_thread = WorkerThread(asyncio.get_event_loop(), sender)
    worker_thread.start()

    logging.info("MargosAppletFactory starting")
    MatePanelApplet.Applet.factory_main(
        "MargosAppletFactory",
        MatePanelApplet.Applet.__gtype__,
        MatePanelApplet.Applet.__gtype__,
        applet_factory,
        sender,
    )
    logging.info("MargosAppletFactory shutting down.")

    worker_thread.drain()
    worker_thread.join()
