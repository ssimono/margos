from margos.models import AppletState


def parse(input: str) -> AppletState:
    """ Parse a text into a fully qualified applet state """
    lines = list(filter(len, input.split("\n")))
    if not len(lines):
        return AppletState("…")

    return AppletState(header=lines[0], menu=lines[1:])
