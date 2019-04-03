APPLET_NAME := Margos

APPLET_ID = fr.sa-web.$(APPLET_NAME)Applet
DBUS_SERVICE =  /usr/share/dbus-1/services/$(APPLET_ID)Factory.service
APPLET_FILE = /usr/share/mate-panel/applets/$(APPLET_ID).mate-panel-applet

BUILDER_IMAGE = margos-builder

render = sed '\
	s|@LOCATION|$(shell pwd)|g;\
	s|@APPLET_NAME|$(APPLET_NAME)|g;\
	s|@APPLET_ID|$(APPLET_ID)|g'

dev-install: APPLET_NAME=MargosDev
dev-install: desktop/*
	$(render) desktop/applet.ini > ${APPLET_FILE}
	ln -fs ${APPLET_FILE} desktop/applet.ini.lnk
	$(render) desktop/dbus.ini > ${DBUS_SERVICE}
	ln -fs ${DBUS_SERVICE} desktop/dbus.ini.lnk

dev-clean:
	rm -f `readlink desktop/*.lnk`
	rm -f desktop/*.lnk

check:
	black --check margos


package:
	rm -rf build
	mkdir -p build
	pipenv run pip freeze > build/requirements.txt
	docker build -f packaging/Dockerfile -t ${BUILDER_IMAGE} .
	docker run --rm --user `id -u` -v "${PWD}/build/:/output" ${BUILDER_IMAGE}
