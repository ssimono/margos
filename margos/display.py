import logging
import gi  # type:ignore

from typing import Optional

gi.require_version("Gtk", "3.0")
gi.require_version("MatePanelApplet", "4.0")

from gi.repository import MatePanelApplet, Gtk, Gdk, GLib, Gio  # type:ignore

from margos.models import (
    AppletConfig,
    AppletAdded,
    AppletRemoved,
    AppletState,
    FactoryDown,
    Notifier,
)

logger = logging.getLogger("margos")


class MargosApplet(Gtk.MenuBar):
    def __init__(self) -> None:
        super().__init__()

        self.connect("button_press_event", self.on_click)

        self._bar_button = Gtk.MenuItem(label="Margos applet")
        self.append(self._bar_button)

        menu = Gtk.Menu()
        menu.append(Gtk.MenuItem(label="First"))
        menu.append(Gtk.MenuItem(label="Second"))
        self._bar_button.set_submenu(menu)

    def on_click(self, target: Gtk.Widget, event: Gdk.Event) -> bool:
        if event.button == Gdk.BUTTON_SECONDARY:
            mate_applet = self.get_parent()
            mate_applet.do_button_press_event(mate_applet, event)
            return True
        return False

    def _render(self, state: AppletState) -> None:
        logger.debug("rendering")
        self._bar_button.set_label(state.header)

    def render(self, state: AppletState) -> None:
        GLib.idle_add(lambda: self._render(state))


def _on_applet_destroy(applet: MargosApplet, notify: Notifier, id_: int) -> None:
    logger.info("Destroying the applet")
    notify(AppletRemoved(id_))


def _applet_factory(
    mate_applet: MatePanelApplet.Applet, iid: str, notify: Notifier
) -> bool:
    config = config_from_gsettings(mate_applet.get_preferences_path())
    if config is None:
        return False

    new_applet = MargosApplet()
    id_ = id(new_applet)

    new_applet.connect_data("destroy", _on_applet_destroy, notify, id_)

    mate_applet.add(new_applet)
    mate_applet.show_all()
    notify(AppletAdded(id_, config, new_applet.render))

    logger.info(f"Applet created with command '{config.command}'")
    return True


def render_loop(iid: str, notify: Notifier) -> None:
    logger.info(f"{iid}Factory starting")
    MatePanelApplet.Applet.factory_main(
        factory_id=f"{iid}Factory",
        out_process=True,
        applet_type=MatePanelApplet.Applet.__gtype__,
        callback=_applet_factory,
        data=notify,
    )
    notify(FactoryDown())
    logging.info(f"{iid}Factory shutting down.")


def config_from_gsettings(pref_path: str) -> Optional[AppletConfig]:
    """ Load an applet configuration from its preference path """
    try:
        settings = Gio.Settings.new_with_path("fr.sa-web.MargosDevApplet", pref_path)
        return AppletConfig(
            command=settings.get_string("command"),
            interval=settings.get_int("interval"),
        )
    except TypeError:
        return None
