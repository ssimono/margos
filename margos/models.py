from typing import Callable, List, NamedTuple, Union


class AppletState(NamedTuple):
    """The current applet content, i.e text, icons, menus items etc"""

    header: str = "…"
    menu: List[str] = []


class AppletConfig(NamedTuple):
    """The applet configuration as defined when added to the panel. Most importantly the command to be run and the refresh intervall"""

    command: str
    interval: int


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


class FactoryDown(NamedTuple):
    """ When all applets are removed and the service shuts down """

    pass


""" All possible events happening at panel level upon user usage """
PanelEvent = Union[AppletAdded, AppletRemoved, FactoryDown]

""" A function callable with a PanelEvent to notify subscribers """
Notifier = Callable[[PanelEvent], None]
