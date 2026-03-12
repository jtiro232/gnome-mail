#!/usr/bin/env python3
"""Summon the Gnome Postal Service."""

from gnome_mail.app import GnomeMailApp

if __name__ == "__main__":
    app = GnomeMailApp()
    app.run()
