#!/bin/sh
# Developer shortcut; Windows end users use the single-file release installer.
exec python "$(dirname "$0")/src/launch.py" "$@"
