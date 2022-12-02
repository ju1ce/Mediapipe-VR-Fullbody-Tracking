@echo off

python\python.exe python\get-pip.py

python\python.exe -m pip install --upgrade pip

python\python.exe -m pip install numpy
python\python.exe -m pip install opencv-python
python\python.exe -m pip install scipy
python\python.exe -m pip install turtle

python\python.exe -m pip install mediapipe

pause
