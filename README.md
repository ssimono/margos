Margos
======

Clone (attempt) of Bitbar/Argos for Mate Desktop. It can create dynamic mate-panel applets
from the output of your own scripts.

Check out the family
--------------------

- [BitBar](https://github.com/matryer/bitbar) for OSX
- [Argos](https://github.com/p-e-w/argos) for Gnome Shell
- [Kargos](https://github.com/lipido/kargos) For KDE Plasma

The aim of Margos is to stay as close as possible to the API shared by the above projects, so all plugins made for one can work with the others.

Compatibility
-------------

Margos currently requires mate >= 1.18, i.e mate-panel migrated to gtk-3. Run `mate-about --version` to check your current version

Development
-----------

Requirements:

- Python 3.7+
- pipenv

Set up the development environment:

    git clone https://github.com/ssimono/margos.git
    pipenv install
    sudo make dev-install # Will copy global applet files to make the local applet available
    export ENVIRONMENT=dev # Use the development version of the applet
    pipenv shell # Start a shell in a virtualenv

You can then start the service: `python -m margos.main`.
Now run `make dev-show`. It will launch mate-applet debug tool to display your applet in a popup. Alternatively you can add *MargosDev* to the panel for real (right click / Add to panel). The service will keep running until you removed all applets from the panel.
