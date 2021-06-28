# MoveNet-VR-Fullbody-Tracking
A test repository using MoveNet and VideoPose3D for fullbody tracking in VR with a single camera.

This is still a work in progress, not meant to be used yet. Main purpose is for other programmers who may have an interest in such a system.

The bat files are configured to use a local instalation of python in /python, but you can also use the scripts directly. You also need the 2d-3d VideoPose3d model to run this, for which you can message me on discord: my username is juice#6370


## How to run:

First, you need to install the ApriltagTrackers driver from my other repo. If you dont have it already, follow the instructions there.

The python libraries required are listed in the install_libraries.bat

Edit the /bin/movenet.py script to set the parameters.

Running the script will first load the libraries, load the models, open the camera and connect to steamvr. This will take some time.

After a while, you will be prompted to put on your headset. Put it on and wait for 5 seconds to calibrate your height.

Use the two sliders on screen to spin and tilt the trackers correctly.
