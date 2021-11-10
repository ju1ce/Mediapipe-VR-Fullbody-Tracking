# Mediapipe-VR-Fullbody-Tracking
A test repository using Mediapipe for fullbody tracking in VR with a single camera.

This is still a work in progress, but an executable is now available for anyone to try out. Compared to my other free fbt project, ApriltagTrackers, this works less acurately, you need far more room and depth detection is not the greatest, but it has the benefit of not needing trackers.

For any questions or bug reports, please write into the ApriltagTrackers discord: https://discord.gg/g2ctkXB4bb

## How to run:

An executable version has now been added to make running this easier. Download it from [here](https://github.com/ju1ce/Mediapipe-VR-Fullbody-Tracking/releases). Unzip the folder anywhere you want.

First, install the driver by running the install_driver.exe from /driver_files.

Before you start the program, put the camera you will be using into a good spot. The camera HAS to see your entire body, and it helps if it is above you tilted downward!

Then, you should be able to run the program with start_mediapipepose.bat file. A setting window should appear, but you probably only want to change the first setting:
- IP or ID of camera: If using IP Webcam on android, this will be an IP address. Enter it in the form http://<ip-here>:8080/video. If using a wired webcam, this will be a number. Usualy 0, but sometimes 1 or 2 etc... If 0 doesnt work, try others.
- Maximum image size: If image is larger than this, it will be downscaled to prevent working with too large images. 800 seems to work fine.
- Offset of HMD to neck: three values, seperated by spaces. Show offset of your neck to the hmd, which is necesary for further calculations. First value is left/right, second is up/down, third is forward/back. Default is 0.2 meters down, 0.1 meter back and should work well enough.
- Smoothing: The smoothing window in seconds. The higher it is, the smoother will motion be, but with more latency.
- Camera latency: The latency of your camera. Increase to reduce delay, but at the cost of more shakyness.
- Rotate camera clockwise/counter clockwise: Rotate the camera input 90° in one direction, or 180° if both are checked.
- Enable experimental foot rotation: Foot rotation! May not work at all angles.
- Enable automatic scale calibration: Disabling this will give you a slider to calibrate your height manualy.
- Enable automatic tilt calibration: Disabling this will give you a slider to calibrate the camera tilts manualy. 
- Enable automatic rotation calibration: Disabling this will give you a slider to calibrate playspace rotation manualy.
  
There are also some DEV options, that you probably dont want to use:
  - Preview skeleton in VR: Instead of spawning just three trackers for legs, the entire skeleton will be spawned and shown 2 meters in front of you. Useful for visualizing how well it works. Dont use for actual gameplay!
  - Spawn trackers for hands: Try to emulate controllers by spawning trackers for your hands. Works pretty bad, so I would recommend against using this.
  
When done, press Save and continue to start the program. It will open the camera and do some other initialization steps. Then, stand upright and still with the headset on and in view of the camera. Look straight ahead. Switch the recalibrate slider to 1 to calibrate your height, camera tilt and rotation automaticaly.
  
If you disabled automatic calibration, use the other sliders to calibrate height, tilt or rotation manualy.

When you are done, you can now play vrchat or any other fbt game of your choice!
  
Your controllers may dissapear or no longer work when you use it the first time. If that happens, restart steamvr.

# MediaPipe version 

Thanks to John_ on the ApriltagTrackers discord, who reminded me that MediaPipe pose does in fact have 3d positions as well, the script was modified to use that version. It seems to be faster, pretty accurate, and should be easier to setup. Beside not needing the 3d model, the instructions on how to use are the same.

The movenet version has now been removed from the repo.


## Information for devs:

The project is configured to run from a local python installation in a /python subdirectory, but that kind of broke in the last few commits so probably better to just use global python and run mediapipepose.py directly.

Any needed libraries are listed in install_libraries.bat.

