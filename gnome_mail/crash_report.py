"""Crash reporting utility for Gnome Mail. Captures system info and recent errors."""

import os
import sys
import platform
import traceback
from datetime import datetime, timezone

from gnome_mail import db
from gnome_mail.constants import DB_DIR


def _get_report_dir():
    """Return the crash report directory, creating it if needed."""
    base = os.path.join(os.path.expanduser("~"), ".local", "share", DB_DIR, "crash_reports")
    os.makedirs(base, exist_ok=True)
    return base


def _get_ollama_info():
    """Gather Ollama version and available models."""
    try:
        import ollama
        models_resp = ollama.list()
        if hasattr(models_resp, "models"):
            models = [m.model for m in models_resp.models]
        elif isinstance(models_resp, dict) and "models" in models_resp:
            models = [m.get("model", m.get("name", "unknown")) for m in models_resp["models"]]
        else:
            models = []
        return {"available": True, "models": models}
    except Exception as e:
        return {"available": False, "error": str(e)}


def _get_recent_errors(limit=10):
    """Fetch recent errored conversations from the database."""
    try:
        conn = db._connect()
        rows = conn.execute(
            "SELECT id, model, subject, error_text, created_at "
            "FROM conversations WHERE status = 'error' "
            "ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"fetch_error": str(e)}]


def generate_crash_report(exception=None):
    """Generate a crash report and save it to disk.

    Args:
        exception: Optional exception object to include. If called from an
                   except block, the current traceback is captured automatically.

    Returns:
        Path to the saved crash report file.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    lines = []
    lines.append("=" * 60)
    lines.append("  GNOME MAIL CRASH REPORT")
    lines.append(f"  Generated: {now.isoformat()}")
    lines.append("=" * 60)
    lines.append("")

    # System info
    lines.append("--- System Information ---")
    lines.append(f"Platform:    {platform.platform()}")
    lines.append(f"Python:      {sys.version}")
    lines.append(f"Executable:  {sys.executable}")
    lines.append(f"Working Dir: {os.getcwd()}")
    lines.append("")

    # Pygame info
    try:
        import pygame
        lines.append("--- Pygame ---")
        lines.append(f"Version:     {pygame.version.ver}")
        if pygame.display.get_init():
            info = pygame.display.Info()
            lines.append(f"Display:     {info.current_w}x{info.current_h}")
        lines.append("")
    except Exception:
        lines.append("--- Pygame: not available ---")
        lines.append("")

    # Ollama info
    ollama_info = _get_ollama_info()
    lines.append("--- Ollama ---")
    if ollama_info["available"]:
        lines.append(f"Status:      Connected")
        lines.append(f"Models:      {', '.join(ollama_info['models']) if ollama_info['models'] else 'none found'}")
    else:
        lines.append(f"Status:      Unavailable")
        lines.append(f"Error:       {ollama_info['error']}")
    lines.append("")

    # Exception details
    lines.append("--- Exception ---")
    if exception:
        lines.append(f"Type:        {type(exception).__name__}")
        lines.append(f"Message:     {exception}")
        lines.append("")
        lines.append("Traceback:")
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        lines.extend(line.rstrip() for line in "".join(tb).splitlines())
    elif sys.exc_info()[1] is not None:
        exc_type, exc_val, exc_tb = sys.exc_info()
        lines.append(f"Type:        {exc_type.__name__}")
        lines.append(f"Message:     {exc_val}")
        lines.append("")
        lines.append("Traceback:")
        tb = traceback.format_exception(exc_type, exc_val, exc_tb)
        lines.extend(line.rstrip() for line in "".join(tb).splitlines())
    else:
        lines.append("No exception provided (manual report).")
    lines.append("")

    # Recent errors from DB
    lines.append("--- Recent Conversation Errors ---")
    recent = _get_recent_errors()
    if recent and "fetch_error" not in recent[0]:
        for err in recent:
            lines.append(f"  [{err['created_at']}] model={err['model']}")
            lines.append(f"    subject: {err['subject']}")
            lines.append(f"    error:   {err['error_text']}")
            lines.append("")
    elif recent and "fetch_error" in recent[0]:
        lines.append(f"  Could not fetch errors: {recent[0]['fetch_error']}")
    else:
        lines.append("  No recent errors found.")
    lines.append("")

    lines.append("=" * 60)
    lines.append("  END OF CRASH REPORT")
    lines.append("=" * 60)

    report_text = "\n".join(lines)

    # Save to file
    report_dir = _get_report_dir()
    filename = f"crash_{timestamp}.txt"
    filepath = os.path.join(report_dir, filename)
    with open(filepath, "w") as f:
        f.write(report_text)

    return filepath
