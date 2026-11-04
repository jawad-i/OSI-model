#!/usr/bin/env bash
set -e

echo "========================================================================"
echo "        RUNNING FULL OSI 7-LAYER AUTOMATED TEST SUITE (LINUX/UBUNTU)"
echo "========================================================================"

echo ""
echo "[STEP 1] Building project binaries with make..."
make all

echo ""
echo "[STEP 2] Testing Standalone C Simulation (osi_sim)..."
./bin/osi_sim "Automated Shell Test 1: Full 7-Layer OSI Simulation"

echo ""
echo "[STEP 3] Testing Live Socket Communication (Client + Server)..."
./bin/osi_server 8085 &
SERVER_PID=$!
sleep 1

./bin/osi_client "Automated Shell Test 2: Live Socket Transmission" 127.0.0.1 8085
wait $SERVER_PID

echo ""
echo "[STEP 4] Testing Python Visualizer (Demo mode)..."
python3 python/visualizer.py --demo --speed 0.01 --message "Automated Shell Test 3: Python Zig-Zag Visualizer"

echo ""
echo "========================================================================"
echo "        ALL OSI MODEL SIMULATION TESTS PASSED SUCCESSFULLY!"
echo "========================================================================"
