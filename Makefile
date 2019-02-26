APPLET_NAME := Margos
APPLET_FQDN := apps.margos.mate.panel.${APPLET_NAME}Applet

DBUS_SERVICE :=  /usr/share/dbus-1/services/${APPLET_FQDN}Factory.service
APPLET_FILE := /usr/share/mate-panel/applets/${APPLET_FQDN}.mate-panel-applet

render := sed 's|@LOCATION|$(shell pwd)|g;s|@FQDN|${APPLET_FQDN}|g'

dev-install: mate-files/*
	$(render) mate-files/applet.ini > ${APPLET_FILE}
	ln -s ${APPLET_FILE} mate-files/applet.ini.lnk
	$(render) mate-files/dbus.ini > ${DBUS_SERVICE}
	ln -s ${DBUS_SERVICE} mate-files/dbus.ini.lnk
