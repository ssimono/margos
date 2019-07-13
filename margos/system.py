from os import remove
from pkg_resources import resource_filename
from subprocess import check_output, check_call
from typing import NamedTuple

APPLETS_FOLDER = "/usr/share/mate-panel/applets"
SERVICES_FOLDER = "/usr/share/dbus-1/services"
SCHEMAS_FOLDER = "/usr/share/glib-2.0/schemas"
COMPILED_SCHEMA = "/usr/share/glib-2.0/schemas/gschemas.compiled"


class MargosConfig(NamedTuple):
    """ Margos cross-applets factory configuration. Helper with the mate applet metadata mangement """

    name: str = "Margos"
    domain: str = "org.mate.panel.applet"
    env: str = "prod"

    @property
    def applet_name(self) -> str:
        return f"{self.name}Applet"

    @property
    def applet_fullname(self) -> str:
        return f"{self.domain}.{self.applet_name}"

    @property
    def factory_name(self) -> str:
        return f"{self.applet_name}Factory"

    @property
    def factory_fullname(self) -> str:
        return f"{self.domain}.{self.factory_name}"


conf = MargosConfig()

applet_file = f"{APPLETS_FOLDER}/{conf.applet_fullname}.mate-panel-applet"
service_file = f"{SERVICES_FOLDER}/{conf.factory_fullname}.service"
schema_file = f"{SCHEMAS_FOLDER}/{conf.applet_fullname}.gschema.xml"


def _recompile_schemas() -> None:
    print("recompiling glib settings schemas...")
    check_call(["glib-compile-schemas", f"{SCHEMAS_FOLDER}/"])


def _render(filename: str, **kwargs: str) -> str:
    with open(resource_filename("margos.resources", filename)) as input:
        return input.read().format(conf=conf, **kwargs)


def install() -> int:
    """ Render the required mate system files and install them """
    bin_path = check_output(["which", "margos"]).decode("utf-8").strip("\n")

    with open(applet_file, "w") as f:
        print(f"writing {applet_file}...")
        f.write(_render("applet.ini"))

    with open(service_file, "w") as f:
        print(f"writing {service_file}...")
        f.write(_render("dbus.ini", bin_path=bin_path))

    with open(schema_file, "w") as f:
        print(f"writing {schema_file}...")
        f.write(_render("schema.xml"))

    _recompile_schemas()

    return 0


def uninstall() -> int:
    """ Deletes the mate system files """
    print(f"deleting {applet_file}...")
    remove(applet_file)
    print(f"deleting {service_file}...")
    remove(service_file)
    print(f"deleting {schema_file}...")
    remove(schema_file)
    return 0
