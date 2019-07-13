Margos
======

Create dynamic Mate Panel applets very easily from the text output of your own scripts! This is a work-in-progress clone of Bitbar/Argos for Mate Desktop.

Check out the family
--------------------

- [BitBar](https://github.com/matryer/bitbar) for OSX
- [Argos](https://github.com/p-e-w/argos) for Gnome Shell
- [Kargos](https://github.com/lipido/kargos) For KDE Plasma

Margos allows you to create desktop applet on Mate, that you can put anywhere on the panel(s) and configure directly with gconf the same way other applets are configured. It therefore ignores meta-information based on script name. It is far from being done, but already outperforming the native mate command applet.

Progress
--------

- [x] Show command output on the panel
- [x] Refresh every x seconds
- [x] Display a list from further lines of output
- [ ] Unlimited recursive submenus
- [ ] Rotation of lines above `---`
- [ ] Line attributes and all subsequent features

Compatibility
-------------

Margos currently requires mate >= 1.18, i.e mate-panel migrated to gtk-3. Run `mate-about --version` to check your current version.
You will also need Python 3.6+ and pip3 on your system.

Installation
------------

1. `sudo pip3 install -U --system margos`
2. `sudo margos install` to make the applet available to the desktop
3. `killall mate-panel` to restart the panel

To uninstall, make sure to clean the system files with `sudo margos uninstall` before removing the python package with pip3.

Usage
-----

Once installed, simply add a new Margos applet on your panel. You can then right-click and set the command you wish to run in the "preferences" menu.
