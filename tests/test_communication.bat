@echo off
echo ========================================================================
echo        RUNNING FULL OSI 7-LAYER AUTOMATED TEST SUITE (WINDOWS)
echo ========================================================================

echo.
echo [STEP 1] Testing Standalone C Simulation (osi_sim.exe)...
bin\osi_sim.exe "Automated Batch Test 1: Full 7-Layer OSI Simulation"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] osi_sim.exe failed!
    exit /b 1
)

echo.
echo [STEP 2] Testing Live Socket Communication (Client + Server)...
start /b bin\osi_server.exe 8085
timeout /t 1 /nobreak >nul
bin\osi_client.exe "Automated Batch Test 2: Live Socket Transmission" 127.0.0.1 8085
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] osi_client.exe failed!
    exit /b 1
)

echo.
echo [STEP 3] Testing Python Visualizer (Demo mode)...
python python\visualizer.py --speed 0.01 --message "Automated Batch Test 3: Python Zig-Zag Visualizer"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python visualizer failed!
    exit /b 1
)

echo.
echo ========================================================================
echo        ALL OSI MODEL SIMULATION TESTS PASSED SUCCESSFULLY!
echo ========================================================================
