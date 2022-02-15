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
- Dont use hip tracker: Disable hip tracking, if you wish to use owotrack for hips instead.
  
There are also some DEV options, that you probably dont want to use:
  - Preview skeleton in VR: Instead of spawning just three trackers for legs, the entire skeleton will be spawned and shown 2 meters in front of you. Useful for visualizing how well it works. Dont use for actual gameplay!
  - Spawn trackers for hands: Try to emulate controllers by spawning trackers for your hands. Works pretty bad, so I would recommend against using this.
  
When done, press Save and continue to start the program. It will open the camera and do some other initialization steps. Then, stand upright and still with the headset on and in view of the camera. Look straight ahead. Switch the recalibrate slider to 1 to calibrate your height, camera tilt and rotation automaticaly.
  
If you disabled automatic calibration, use the other sliders to calibrate height, tilt or rotation manualy.

When you are done, you can now play vrchat or any other fbt game of your choice!
  
Your controllers may dissapear or no longer work when you use it the first time. If that happens, restart steamvr.
  
Automatic scale calibration may not work for some people, mostly on lighthouse tracked headsets. If you notice your feet are far above the ground, disable automatic scale calibration and use the slider instead.

## Troubleshooting
  
**The app crashes with an ImportError: DLL load failed:**
 
This seems to be a problem with some windows "N" versions, which seem to miss some media features: Installing the media feature pack should fix it. Read more about it here: https://stackoverflow.com/a/54321350
  
**The tracking is unuseably bad:**
  
While the tracking is not perfect even under ideal conditions due to no depth information, there is still a few things you can do to improve it:
  
- Make sure that your entire body is seen on the camera, including your head!
- Make sure there is enough light in the room. and there shouldnt be any light sources behind you, such as any bright windows. Try to get as much lighting as you can from the direction of the camera.
- Mind what you wear: you need to be in contrast with the background, so dont wear clothes the same color as the background and avoid clothes with patterns.
- Play with the smoothing and latency parameters a bit. To learn what exactly they do, we have some nice graphs [here](https://github.com/ju1ce/April-Tag-VR-FullBody-Tracker/wiki/Refining-parameters).
 
**All the trackers are 2 meters away from me:**
  
The DEV: Preview skeleton in VR option will do this in order to preview the tracking, sort of like a mirror. This makes the tracking unusable for games though, so disable this option. And restart SteamVR after doing so.
  
**The trackers are way too high:**
  
If the trackers are far off the ground, or even above you, height calibration seems to have failed. Try to disable automatic scale calibration. This should enable a new slider to calibrate your height manualy.
  
**Trackers dont allign with my body:**
  
For automatic calibration, make sure that you stand straight and look straight ahead or some parts may not be calibrated well enough. If automatic calibration just doesnt seem to work, you can try to disable parts of it: start with scale calibration, then rotation calibration, and finaly tilt calibration. There will be more parameters to calibrate manualy, but it should still work.
  
**Trackers don't show up in VR, status window says "Move to wake up trackers"**
  
This is usualy caused when smoothing window is too low, or camera latency is too high. Set them back to default values (smoothing window 0.5, camera latency 0.05) and adjust the values in smaller steps to find out the optimal parameters! Usualy, smoothing window can go down to 0.3, and camera latency should usualy not be over 0.1.

Explanation: The smoother needs at least 5 previous frames to work. If it has less than that, it will fail to estimate pose, causing the described problem. Example: with a window of 0.5 and proccesing time per frame of 0.05, the smoother will have on avarage 10 frames to work with, which will work fine. With a window of 0.2, it will have on avarage 4 frames to work with, which is not enough, and trackers will not wake up.
  
## Other tips:
  
- A wider FOV can help you have more room to move around, and ensure you can stand closer to the camera. If your camera/phone supports that, make sure to use it!

# MediaPipe version 

Thanks to John_ on the ApriltagTrackers discord, who reminded me that MediaPipe pose does in fact have 3d positions as well, the script was modified to use that version. It seems to be faster, pretty accurate, and should be easier to setup. Beside not needing the 3d model, the instructions on how to use are the same.

The movenet version has now been removed from the repo.


## Information for devs:

The project is configured to run from a local python installation in a /python subdirectory, but that kind of broke in the last few commits so probably better to just use global python and run mediapipepose.py directly.

Any needed libraries are listed in install_libraries.bat.

