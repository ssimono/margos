#! /usr/bin/env python3

import gi
gi.require_version('MatePanelApplet', '4.0')

from gi.repository import MatePanelApplet
from gi.repository import Gtk


def applet_fill(applet):
    label = Gtk.Label(label="Hello World")
    applet.add(label)
    applet.show_all()

def applet_factory(applet, iid, data):
    if iid != "MargosApplet":
       return False

    applet_fill(applet)

    return True

MatePanelApplet.Applet.factory_main("MargosAppletFactory",
                                MatePanelApplet.Applet.__gtype__,
                                MatePanelApplet.Applet.__gtype__,
                                applet_factory, None)
