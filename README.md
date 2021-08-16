# Mediapipe-VR-Fullbody-Tracking
A test repository using Mediapipe for fullbody tracking in VR with a single camera.

This is still a work in progress, but an executable is now available for anyone to try out. Compared to my other free fbt project, ApriltagTrackers, this works less acurately, you need far more room and depth detection is not the greatest, but it has the benefit of not needing trackers.

For any questions or bug reports, please write into the ApriltagTrackers ![discord](https://discord.gg/g2ctkXB4bb)

## How to run:

An executable version has now been added to make running this easier. Download it from [here](https://github.com/ju1ce/Mediapipe-VR-Fullbody-Tracking/releases). Unzip the folder anywhere you want.

First, install the driver by running the install_driver.exe from /driver_files.

Before you start the program, put the camera you will be using into a good spot. The camera HAS to see your entire body, and it helps if it is above you tilted downward!

Then, you should be able to run the program with start_mediapipepose.bat file. A setting window should appear, but you probably only want to change the first setting:
- IP or ID of camera: If using IP Webcam on android, this will be an IP address. If using a wired webcam, this will be a number. Usualy 0, but sometimes 1 or 2 etc... If 0 doesnt work, try others.
- Maximum image size: If image is larger than this, it will be downscaled to prevent working with too large images. 800 seems to work fine.
- Offset of HMD to neck: three values, seperated by spaces. Show offset of your neck to the hmd, which is necesary for further calculations. First value is left/right, second is up/down, third is forward/back. Default is 0.2 meters down, 0.1 meter back and should work well enough.
- Preview whole skeleton: Instead of spawning just three trackers for legs, the entire skeleton will be spawned and shown 2 meters in front of you. Useful for visualizing how well it works.
- Dont wait for HMD: Starts detection without waiting for you to put on the HMD. Useful if you already wear it or if you just want to see how it works without VR.
- Rotate camera clockwise/counter clockwise: Rotate the camera input 90° in one direction, or 180° if both are checked.

When done, press Save and continue to start the program. It will open the camera and do some other initialization steps, then prompt you to put on your headset (if you are already wearing it, just move it downward for a second to detect it). Then, stand upright and still with the headset on and in view of the camera. After 5 seconds, your height will be calibrated and the trackers should appear in VR.

Automatic calibration isnt done yet, so you now have to manualy correct your rotation. The camera feed should appear on your desktop with two sliders. The first slider controlls your rotation around the up axis, and the second one controlls the forward/backward tilt. Use them to align the trackers in vr with your feet.

When you are done, you can now play vrchat or any other fbt game of your choice!

# MediaPipe version 

Thanks to John_ on the ApriltagTrackers discord, who reminded me that MediaPipe pose does in fact have 3d positions as well, the script was modified to use that version. It seems to be faster, pretty accurate, and should be easier to setup. Beside not needing the 3d model, the instructions on how to use are the same.

The movenet version has now been removed from the repo.


## Information for devs:

The project is configured to run from a local python installation in a /python subdirectory, but that kind of broke in the last few commits so probably better to just use global python and run mediapipepose.py directly.

Any needed libraries are listed in install_libraries.bat.

## TODO:

Mediapipe actualy returns feet rotation as well, which I currently ignore. Whether it is accurate enough to actualy use should be tested, however.

While calibrating with sliders is pretty fast and easy, automatic calibration using controller positions should be possible as well.

