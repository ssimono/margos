from typing import Callable, List, NamedTuple, Union


class AppletState(NamedTuple):
    """The current applet content, i.e text, icons, menus items etc"""

    header: str = "…"
    menu: List[str] = []


class AppletConfig(NamedTuple):
    """The applet configuration as defined when added to the panel. Most importantly the command to be run and the refresh interval """

    command: str
    interval: int


def validate_applet_config(**kwargs: str) -> Union[AppletConfig, ValueError]:
    """check for sanity and semantics of arguments try to build an AppletConfig"""
    if "command" not in kwargs:
        return ValueError("command missing")
    if not len(kwargs["command"].strip()):
        return ValueError("command empty")
    try:
        int_erval = int(kwargs["interval"])
        if int_erval < 1:
            return ValueError("interval under minimum of 1 second")
        if int_erval > 86400:
            return ValueError("interval over maximum of 1 day")
    except ValueError as e:
        return e
    except KeyError:
        return ValueError("interval missing")

    return AppletConfig(kwargs["command"].strip(), int_erval)


""" A function taking an AppletState with enough information to render the applet """
Renderer = Callable[[AppletState], None]


class AppletAdded(NamedTuple):
    """When a new applet is added to the panel"""

    id_: int
    config: AppletConfig
    render: Renderer


class AppletRemoved(NamedTuple):
    """When an applet is removed from the panel"""

    id_: int


class ConfigUpdated(NamedTuple):
    id_: int
    config: AppletConfig


class FactoryDown(NamedTuple):
    """ When all applets are removed and the service shuts down """

    pass


""" All possible events happening at panel level """
PanelEvent = Union[AppletAdded, AppletRemoved, ConfigUpdated, FactoryDown]

""" A function callable with a PanelEvent to notify subscribers """
Notifier = Callable[[PanelEvent], None]
