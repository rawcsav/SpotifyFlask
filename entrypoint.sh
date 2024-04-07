#!/bin/sh

# Update permissions for /newutil to ensure 'newutil' user can access all files and directories
chown -R rawcon:rawcon /rawcon

# Execute the command specified in the Dockerfile's CMD
exec "$@"
