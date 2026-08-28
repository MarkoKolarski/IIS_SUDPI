#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Windows terminale (cp1252 i sl.) ne mogu da ispišu ćirilične/dijakritičke
    # znakove (č, ć, š, ž...) koje logeri/print pozivi u projektu koriste, pa
    # bez ovoga svaka takva poruka baca UnicodeEncodeError. Prisiljava UTF-8.
    for stream_name in ('stdout', 'stderr'):
        stream = getattr(sys, stream_name)
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='backslashreplace')
            except Exception as exc:
                print(f"[manage.py] Nije uspelo reconfigure({stream_name}, utf-8): {exc}", file=sys.stderr)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IIS_SUDPI.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
