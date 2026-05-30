@echo off
cd /d "%~dp0.."
".\.venv\Scripts\streamlit.exe" run frontend/app.py --server.address 127.0.0.1 --server.port 8501
