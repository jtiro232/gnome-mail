#!/usr/bin/env python3
"""Summon the Gnome Postal Service."""

from gnome_mail.app import GnomeMailApp

if __name__ == "__main__":
    try:
        app = GnomeMailApp()
        app.run()
    except Exception as exc:
        from gnome_mail.crash_report import generate_crash_report
        report_path = generate_crash_report(exc)
        print(f"\nGnome Mail crashed! A crash report has been saved to:\n  {report_path}\n")
        raise
