@echo off
title JARVIS SUPERBRAIN SYSTEM LAUNCHER
color 0A

echo ===================================================
echo         INITIALIZING INFRASTRUCTURE & DATABASES
echo ===================================================
echo Starting Ollama AI Engine with Expanded Memory...

:: Add this line to increase the context limit to 32k tokens
set OLLAMA_CONTEXT_LENGTH=32768

start "Ollama" /min "C:\Users\Admin\AppData\Local\Programs\Ollama\ollama app.exe"
timeout /t 3 /nobreak

echo Starting Redis Neural Link...
start "Redis Server" /min "C:\Program Files\Redis\redis-server.exe"
timeout /t 3 /nobreak

echo Starting ChromaDB Vector Storage...
start "ChromaDB" /min cmd /c "chroma run --host localhost --port 8000"
timeout /t 5 /nobreak

echo ===================================================
echo          LAUNCHING LITELLM AI ROUTER
echo ===================================================
echo Starting LiteLLM Proxy Gate...
start "LiteLLM Router" /min cmd /c "litellm --config C:\jarvis\config\litellm_config.yaml --port 4000"
timeout /t 5 /nobreak

echo ===================================================
echo          LAUNCHING JARVIS CORE MODULES
echo ===================================================
echo Starting Bot A Master Brain (Port 6001 + Market Tasks)...
start "JARVIS Bot A" cmd /k "cd /d C:\jarvis\bot_a && python bot_a.py"
timeout /t 5 /nobreak

echo Starting Execution Trading Bot (Port 6003)...
start "Trading Bot" cmd /k "cd /d C:\jarvis\trading_bot && python trading_bot.py"
timeout /t 5 /nobreak

echo Starting OpenClaw Agent Gateway...
start "OpenClaw Gateway" cmd /k "cd /d C:\openclaw && openclaw gateway run"
timeout /t 3 /nobreak

echo Starting System Live Dashboard...
start "Dashboard UI" /min cmd /c "cd /d C:\jarvis\dashboard && streamlit run dashboard.py --server.port 8501"

echo.
echo ===================================================
echo       ALL SYSTEMS CHANNELS INITIALIZED SAFELY
echo ===================================================
echo Core Engine Port Map:
echo  - LiteLLM: http://localhost:4000
echo  - Master Brain: http://localhost:6001
echo  - Trading Bot: http://localhost:6003
echo  - OpenClaw UI: http://127.0.0.1:18789
echo  - Dashboard: http://localhost:8501
echo ===================================================
pause