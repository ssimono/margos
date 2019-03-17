#! /usr/bin/env python3

import gi
import logging

import asyncio
import threading

gi.require_version("Gtk", "2.0")
gi.require_version("MatePanelApplet", "4.0")

from gi.repository import MatePanelApplet
from gi.repository import Gtk
from gi.repository import GObject

from worker import WorkerThread



class MargosButton(Gtk.MenuBar):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.sender_listener = None
        self._bar_button = Gtk.MenuItem(label="Margos applet")
        self.append(self._bar_button)

        menu = Gtk.Menu()
        menu.append(Gtk.MenuItem(label="First"))
        menu.append(Gtk.MenuItem(label="Second"))
        self._bar_button.set_submenu(menu)

    def on_render(self, sender, cmd, value):
        if cmd == self.cmd:
            self._bar_button.set_label(value)


i = 0


def applet_factory(applet, iid, sender):
    if iid != "MargosApplet":
        return False

    global i

    button = MargosButton(("date", "uptime", "fortune")[i])
    applet.add(button)
    sender.add_applet(button)
    i += 1

    applet.show_all()
    logging.info("Applet created with command '{}'".format(button.cmd))
    return True


class Sender(GObject.GObject):
    def __init__(self):
        super().__init__()
        self.commands = set()

    def add_applet(self, margos_button):
        margos_button.sender_listener = sender.connect(
            "margos_render", margos_button.on_render
        )
        margos_button.connect("destroy", self.on_button_destroy)
        self.commands.add(margos_button.cmd)

    def on_button_destroy(self, margos_button):
        logging.info("Destroying the button")
        logging.info(margos_button.sender_listener)
        self.commands.remove(margos_button.cmd)
        self.disconnect(margos_button.sender_listener)


GObject.type_register(Sender)
GObject.signal_new(
    "margos_render",
    Sender,
    GObject.SignalFlags.RUN_FIRST,
    GObject.TYPE_NONE,
    (GObject.TYPE_GSTRING, GObject.TYPE_GSTRING),
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
