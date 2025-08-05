@echo off
REM Batch script to run all three local minima experiments sequentially.

ECHO.
ECHO ==================================================
ECHO      STARTING AETHEROS EXPERIMENT SUITE
ECHO ==================================================
ECHO.

ECHO.
ECHO --- [1/3] RUNNING CONTROL TEST (NO AETHER) ---
ECHO.
python local_minima_test.py --os none

ECHO.
ECHO --- [2/3] RUNNING STANDARD AETHEROS TEST ---
ECHO.
python local_minima_test.py --os aether

ECHO.
ECHO --- [3/3] RUNNING BOYD E-M AETHEROS TEST ---
ECHO.
python local_minima_test.py --os boyd

ECHO.
ECHO ==================================================
ECHO                  ALL TESTS COMPLETE
ECHO ==================================================
ECHO.

PAUSE
