@echo off
set PORT=8000
gunicorn server:app --bind 0.0.0.0:%PORT%