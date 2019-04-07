import logging
import gi
from os import getpid

gi.require_version("Gtk", "3.0")
gi.require_version("MatePanelApplet", "4.0")

from gi.repository import MatePanelApplet
from gi.repository import Gtk
from gi.repository import GObject


i = 0


class MargosApplet(Gtk.MenuBar):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self._bar_button = Gtk.MenuItem(label="Margos applet")
        self.append(self._bar_button)

        menu = Gtk.Menu()
        menu.append(Gtk.MenuItem(label="First"))
        menu.append(Gtk.MenuItem(label="Second"))
        self._bar_button.set_submenu(menu)

        self.connect("margos_render", self.on_render)

    def on_render(self, emitter, state):
        self._bar_button.set_label(state)


GObject.type_register(MargosApplet)
GObject.signal_new(
    "margos_render",
    MargosApplet,
    GObject.SignalFlags.RUN_FIRST,
    GObject.TYPE_NONE,
    (GObject.TYPE_GSTRING,),
)


class Router:
    def __init__(self):
        super().__init__()
        self.schedules = set()
        self._applets = {}

    def render(self, schedule, state):
        self._applets.get(schedule).emit("margos_render", state)

    def add_applet(self, applet):
        self.schedules.add(applet.cmd)
        self._applets[applet.cmd] = applet
        applet.connect("destroy", self._on_applet_destroy)

    def _on_applet_destroy(self, applet):
        logging.info("Destroying the applet")
        self.schedules.remove(applet.cmd)


def _applet_factory(mate_applet, iid, router):
    # if iid != IID:
    #     return False

    global i

    applet = MargosApplet(("date", "uptime", "fortune")[i])
    mate_applet.add(applet)
    router.add_applet(applet)
    i += 1

    mate_applet.show_all()
    logging.info("Applet created with command '{}'".format(applet.cmd))
    return True


def render_loop(iid, sender):
    logging.info(f"{iid}Factory starting - pid {getpid()}")
    MatePanelApplet.Applet.factory_main(
        f"{iid}Factory",
        MatePanelApplet.Applet.__gtype__,
        MatePanelApplet.Applet.__gtype__,
        _applet_factory,
        sender,
    )
    logging.info(f"{iid}Factory shutting down.")
