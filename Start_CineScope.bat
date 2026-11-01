@echo off
title CineScope - Movie Ratings and Genre Trends
echo ===================================================
echo   Starting CineScope Movie Analytics Dashboard...
echo ===================================================
echo Opening in your browser at http://localhost:8501 ...
echo (Do not close this window while using the website)
echo ===================================================
cd /d "%~dp0"
python -m streamlit run app.py --server.port 8501
pause
