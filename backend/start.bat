@echo off
set PORT=8000
gunicorn app:app --bind 0.0.0.0:$PORT