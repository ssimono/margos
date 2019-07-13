dev-show:
	mate-panel-test-applets --iid MargosAppletFactory::MargosApplet --prefs-path /tmp/
.PHONY: dev-show

check:
	mypy margos
	pyflakes margos
	black --check margos

test:
	python3 -m unittest
