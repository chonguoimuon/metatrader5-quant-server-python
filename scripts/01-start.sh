#!/bin/bash

# Get the current user's UID and GID
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)

# Change ownership of the Wine prefix directory to the current user
sudo chown -R "${CURRENT_UID}:${CURRENT_GID}" /config/.wine

# Source common variables and functions
source /scripts/02-common.sh

# Run installation scripts
/scripts/03-install-mono.sh
/scripts/04-install-mt5.sh
/scripts/05-install-python.sh
/scripts/06-install-libraries.sh

# Start servers
/scripts/07-start-wine-flask.sh

# Keep the script running
tail -f /dev/null