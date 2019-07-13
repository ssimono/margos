import logging
import gi  # type:ignore

from functools import partial
from pkg_resources import resource_filename
from typing import List, Optional, Tuple

gi.require_version("Gtk", "3.0")
gi.require_version("MatePanelApplet", "4.0")

from gi.repository import MatePanelApplet, Gtk, Gdk, GLib, Gio  # type:ignore

from margos.system import conf
from margos.models import (
    AppletConfig,
    AppletAdded,
    AppletRemoved,
    AppletState,
    ConfigUpdated,
    FactoryDown,
    Notifier,
    validate_applet_config,
)

logger = logging.getLogger("margos")


class MargosApplet(Gtk.MenuBar):
    def __init__(self) -> None:
        super().__init__()

        self.connect("button_press_event", self.on_click)

        self._bar_button = Gtk.MenuItem(label="Margos applet")
        self._bar_button.set_submenu(Gtk.Menu())
        self.append(self._bar_button)

    def on_click(self, target: Gtk.Widget, event: Gdk.Event) -> bool:
        if event.button == Gdk.BUTTON_SECONDARY:
            mate_applet = self.get_parent()
            mate_applet.do_button_press_event(mate_applet, event)
            return True
        return False

    def _render(self, state: AppletState) -> None:
        logger.debug("rendering")
        self._bar_button.set_label(state.header)
        menu = self._bar_button.get_submenu()
        menuItems = menu.get_children()

        # Update current items
        for (line, menuItem) in zip(state.menu, menuItems):
            menuItem.set_label(line)

        # Add missing items
        for line in state.menu[len(menuItems) :]:
            print(f"adding {line}")
            new_item = Gtk.MenuItem(label=line)
            menu.append(new_item)
            new_item.show()

        # Remove extra items
        for item in menuItems[len(state.menu) :]:
            menu.remove(item)

    def render(self, state: AppletState) -> None:
        GLib.idle_add(lambda: self._render(state))


def _on_dialog_response(target: Gtk.Widget, response_type: int) -> None:
    if response_type == int(Gtk.ResponseType.DELETE_EVENT):
        target.close()


def _pref_dialog(
    mate_applet: MatePanelApplet.Applet, pref_btn: Gtk.Action, notify: Notifier
) -> None:
    builder = Gtk.Builder()
    builder.add_from_file(
        resource_filename("margos.resources", "preferences_dialog.xml")
    )

    def on_pref_apply(value_widgets: List[Gtk.Editable], apply_btn: Gtk.Widget) -> None:
        values = {w.get_name(): w.get_text() for w in value_widgets}
        new_config = validate_applet_config(**values)
        if isinstance(new_config, AppletConfig):
            if save_to_gsettings(mate_applet.get_preferences_path(), new_config):
                notify(ConfigUpdated(id(mate_applet.get_child()), new_config))
                apply_btn.get_ancestor(Gtk.Dialog).close()
        else:
            logging.error(new_config)  # TODO: display the error back

    def on_pref_cancel(cancel_button: Gtk.Widget) -> None:
        cancel_button.get_ancestor(Gtk.Dialog).close()

    current_config = config_from_gsettings(mate_applet.get_preferences_path())
    command_widget = builder.get_object("margos_command")
    interval_widget = builder.get_object("margos_interval")

    if current_config:
        command_widget.set_text(current_config.command)
        interval_widget.set_text(str(current_config.interval))

    builder.connect_signals(
        {
            "on_pref_cancel": on_pref_cancel,
            "on_pref_apply": partial(on_pref_apply, [command_widget, interval_widget]),
        }
    )
    builder.get_object("pref_dialog").show_all()


def _on_applet_destroy(applet: MargosApplet, notify: Notifier, id_: int) -> None:
    logger.info("Destroying the applet")
    notify(AppletRemoved(id_))


def _make_action_group(
    mate_applet: MatePanelApplet.Applet, notify: Notifier
) -> Tuple[str, Gtk.ActionGroup]:
    actions = [
        (
            "PrefsAction",
            Gtk.STOCK_PROPERTIES,
            "Preferences",
            None,
            None,
            partial(_pref_dialog, mate_applet),
        )
    ]

    action_group = Gtk.ActionGroup("applet_config")
    action_group.add_actions(actions, notify)

    xml = "\n".join(
        [f'<menuitem action="{a.get_name()}" />' for a in action_group.list_actions()]
    )

    return (xml, action_group)


def _applet_factory(
    mate_applet: MatePanelApplet.Applet, iid: str, notify: Notifier
) -> bool:
    if iid != conf.applet_name:
        return False

    pref_path = mate_applet.get_preferences_path()
    config = config_from_gsettings(pref_path)
    if config is None:
        return False

    new_applet = MargosApplet()
    id_ = id(new_applet)

    new_applet.connect_data("destroy", _on_applet_destroy, notify, id_)

    mate_applet.add(new_applet)
    mate_applet.setup_menu(*_make_action_group(mate_applet, notify))
    mate_applet.show_all()

    notify(AppletAdded(id_, config, new_applet.render))
    logger.info(f"Applet created with command '{config.command}'")

    return True


def render_loop(notify: Notifier) -> None:
    logger.info(f"{conf.name} starting")
    MatePanelApplet.Applet.factory_main(
        factory_id=conf.factory_name,
        out_process=True,
        applet_type=MatePanelApplet.Applet.__gtype__,
        callback=_applet_factory,
        data=notify,
    )
    notify(FactoryDown())
    logging.info(f"{conf.name} shutting down.")


def config_from_gsettings(pref_path: str) -> Optional[AppletConfig]:
    """ Load an applet configuration from its preference path """
    try:
        settings = Gio.Settings.new_with_path(conf.applet_fullname, pref_path)
        return AppletConfig(
            command=settings.get_string("command"),
            interval=settings.get_int("interval"),
        )
    except TypeError:
        return None


def save_to_gsettings(pref_path: str, config: AppletConfig) -> bool:
    """ Save an applet configuration to gsettings """
    try:
        settings = Gio.Settings.new_with_path(conf.applet_fullname, pref_path)
        settings.set_string("command", config.command)
        settings.set_int("interval", config.interval)
        return True
    except Exception as e:
        logging.error(e)
        return False
