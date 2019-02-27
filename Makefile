APPLET_NAME := Margos
APPLET_FQDN := apps.margos.mate.panel.${APPLET_NAME}Applet

DBUS_SERVICE :=  /usr/share/dbus-1/services/${APPLET_FQDN}Factory.service
APPLET_FILE := /usr/share/mate-panel/applets/${APPLET_FQDN}.mate-panel-applet

render := sed 's|@LOCATION|$(shell pwd)|g;s|@FQDN|${APPLET_FQDN}|g'

dev-install: desktop/*
	$(render) desktop/applet.ini > ${APPLET_FILE}
	ln -fs ${APPLET_FILE} desktop/applet.ini.lnk
	$(render) desktop/dbus.ini > ${DBUS_SERVICE}
	ln -fs ${DBUS_SERVICE} desktop/dbus.ini.lnk

check:
	black --check margos
