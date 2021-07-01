# MoveNet-VR-Fullbody-Tracking
A test repository using MoveNet and VideoPose3D for fullbody tracking in VR with a single camera.

This is still a work in progress, not meant to be used yet. Main purpose is for other programmers who may have an interest in such a system.

The bat files are configured to use a local instalation of python in /python, but you can also use the scripts directly. You also need the 2d-3d VideoPose3d model to run this, for which you can message me on discord: my username is juice#6370

# MediaPipe version 

Thanks to John_ on the ApriltagTrackers discord, who reminded me that MediaPipe pose does in fact have 3d positions as well, the script was modified to use that version. It seems to be faster, pretty accurate, and should be easier to setup. Beside not needing the 3d model, the instructions on how to use are the same.


## How to run:

First, you need to install the ApriltagTrackers driver from my other repo. If you dont have it already, follow the instructions there.

The python libraries required are listed in the install_libraries.bat. The mediapipe version does not need pytorch, however.

Edit the /bin/movenet.py script to set the parameters, or /bin/mediapipe.py for the mediapipe version.

Running the script will first load the libraries, load the models, open the camera and connect to steamvr. This can take some time.

After a while, you will be prompted to put on your headset. Put it on, stand straight, and wait for 5 seconds to calibrate your height.

Use the two sliders on screen to spin and tilt the trackers correctly.

## TODO:

Mediapipe actualy returns feet rotation as well, which I currently ignore. Whether it is accurate enough to actualy use should be tested, however.

While calibrating with sliders is pretty fast and easy, automatic calibration using controller positions should be possible as well.

