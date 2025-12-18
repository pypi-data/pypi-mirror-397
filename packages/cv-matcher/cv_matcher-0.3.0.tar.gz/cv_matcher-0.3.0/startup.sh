#!/bin/bash

# Startup script for Azure App Service
echo "Starting CV Matcher application..."

# Set environment variables if not already set
export PYTHONUNBUFFERED=1
export GRADIO_SERVER_NAME=0.0.0.0
export GRADIO_SERVER_PORT=${PORT:-7860}

# Start the application
python launch_ui.py
