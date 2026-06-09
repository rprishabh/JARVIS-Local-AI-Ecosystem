@echo off
title STOPPING JARVIS
color 0C

echo ===================================================
echo           HALTING ALL JARVIS CORE ENGINES
echo ===================================================
echo.

echo Stopping Python applications (Dashboard, Bot A, Trading Bot)...
taskkill /f /im python.exe 2>nul

echo Stopping LiteLLM Router...
taskkill /f /im litellm.exe 2>nul

echo Stopping ChromaDB database...
taskkill /f /im chroma.exe 2>nul

echo Stopping Redis Neural Link...
taskkill /f /im redis-server.exe 2>nul

echo Stopping Ollama AI Engine...
taskkill /f /im ollama.exe 2>nul

echo.
echo ===================================================
echo           ALL PROCESSES SUCCESSFULLY TERMINATED
echo ===================================================
echo.
pause