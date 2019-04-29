import logging
import gi
from os import getpid
from threading import Lock

gi.require_version("Gtk", "3.0")
gi.require_version("MatePanelApplet", "4.0")

from gi.repository import MatePanelApplet
from gi.repository import Gtk
from gi.repository import GLib


logger = logging.getLogger("margos")


class MargosApplet(Gtk.MenuBar):
    def __init__(self):
        super().__init__()
        self._bar_button = Gtk.MenuItem(label="Margos applet")
        self.append(self._bar_button)

        menu = Gtk.Menu()
        menu.append(Gtk.MenuItem(label="First"))
        menu.append(Gtk.MenuItem(label="Second"))
        self._bar_button.set_submenu(menu)

    def on_click(self, target, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            mate_applet = self.get_parent()
            mate_applet.do_button_press_event(mate_applet, event)
            return True

    def render(self, state):
        logger.debug("rendering")
        self._bar_button.set_label(state)


class Router:
    def __init__(self):
        self._applets = {}
        self._lock = Lock()
        self.i = 0

    def render(self, schedule, state):
        GLib.idle_add(lambda: self._applets.get(schedule).render(state))

    def make_applet(self, mate_applet, iid):
        new_applet = MargosApplet()
        new_cmd = ("date", "uptime", "fortune")[self.i]

        new_applet.connect_data("destroy", self._on_applet_destroy, new_cmd)

        with self._lock:
            self._applets.update({new_cmd: new_applet})

        logging.info("Applet created with command '{}'".format(new_cmd))
        self.i += 1

        mate_applet.add(new_applet)
        mate_applet.show_all()
        return True

    @property
    def schedules(self):
        with self._lock:
            scheds = set(self._applets.keys())
        return scheds

    def _on_applet_destroy(self, applet, cmd):
        logging.info("Destroying the applet")
        self._applets.pop(cmd)


def render_loop(iid, router):
    logging.info(f"{iid}Factory starting - pid {getpid()}")
    MatePanelApplet.Applet.factory_main(
        f"{iid}Factory", True, MatePanelApplet.Applet.__gtype__, router.make_applet
    )
    logging.info(f"{iid}Factory shutting down.")
