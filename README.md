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

Development
-----------

Requirements:

- Python 3.6+
- pipenv

Set up the development environment:

    git clone https://github.com/ssimono/margos.git
    pipenv install
    sudo make dev-install # Will copy global applet files to make the local applet available

You can then start the service: `pipenv run ./margos-applet.py` and add the *Margos* applet to the panel (right click / Add to panel). The program will keep running until you removed all applets from the panel.
