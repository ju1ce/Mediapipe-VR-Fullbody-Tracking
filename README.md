# Mediapipe-VR-Fullbody-Tracking
A test repository using Mediapipe for fullbody tracking in VR with a single camera.

This is still a work in progress, but an executable is now available for anyone to try out. Compared to my other free fbt project, ApriltagTrackers, this works less acurately, you need far more room and depth detection is not the greatest, but it has the benefit of not needing trackers and being far easier to setup and use!

---
### **For any questions or bug reports, please write into the [ApriltagTrackers discord!](https://discord.gg/g2ctkXB4bb)**
---

## Using VRChat OSC:

The newest beta release supports VRChats OSC trackers. It should be possible to use it for FBT on standalone quest VRChat. To download it, go to the [releases](https://github.com/ju1ce/Mediapipe-VR-Fullbody-Tracking/releases) tab and download the 0.7 beta version.

To use OSC, change the backend parameter to VRChat OSC. If you will run VR on the same PC as mediapipepose, or you will use Quest 2 through link/VD/ALVR you can leave the IP at default. If you use quest standalone, enter the local IP address of your quest. If you use standalone, make sure to enable the WebUI option as well. 

The process of using the OSC version is the same as regular, with a few differences:
- When doing automatic calibration, it will not adjust Y rotation. Adjust it manualy until the skeleton aligns with your body.
- Smoothing window is not supported, adjust smoothing using the Additional Smoothing parameter instead. It works better anyway

### The WebUI:

If you are on Quest standalone, you cannot access the normal UI while wearing the headset, making calibration that way quite difficult. Thats where you enable the webui.

When starting up detection, the console will log the IP and port that you need to connect to. Open the web browser on Quest, enter the IP and port (NOT the 127.0.0.1 one) into the address bar, and open the page. A minimal UI should open, giving you control over the calibration parameters.

**NOTE:** This build is still in beta, so make sure to report any issues either in the github issues, or on the [discord](https://discord.gg/g2ctkXB4bb).

## How to run:

An executable version has now been added to make running this easier. Download it from [here](https://github.com/ju1ce/Mediapipe-VR-Fullbody-Tracking/releases). Unzip the folder anywhere you want.

First, install the driver by running the install_driver.exe from /driver_files.

Before you start the program, put the camera you will be using into a good spot. The camera HAS to see your entire body, and it helps if it is above you tilted downward!

Then, you should be able to run the program with start_mediapipepose.bat file. A setting window should appear with the initial settings:

- IP or ID of camera: If using IP Webcam on android, this will be an IP address. Enter it in the form http://<ip-here>:8080/video. If using a wired webcam, this will be a number. Usualy 0, but sometimes 1 or 2 etc... If 0 doesnt work, try others.
- Camera width and height: The resolution that the camera will be opened with. Higher values do not mean better tracking, so you should leave this at default unless you have issues with the camera, such as not opening or being really zoomed in.
- Attempt to open camera settings: Try to open an additional window with settings for the camera, such as gain, exposure... 
- Enable experimental foot rotation: Foot rotation! May not work at all angles, however, so you may want to disable this.
- Disable hip tracker: Disable hip tracking, if you wish to use owotrack for hips instead.
  
- Enable advanced mode: Advanced mode enables you to edit more settings. Only enable this after getting used to the software, as the additional settings can break detection if used incorrectly!
- Save and continue: Save the settings and start detection!
  
After pressing the save and continue button, a window with the camera feed and a window with runtime settings will appear! If they do not, check troubleshooting steps below.
  
Now, put on your headset and go into vr, but dont launch vrhcat yet: we still need to calibrate the tracking.
  
To do so, open your SteamVR dashboard (from inside vr), navigate to your desktop, and to the settings window. To calibrate, stand straight, look straight ahead, and press the Recalibrate button. Your head must look straight forward from your body, or rotation will be calibrated wrong! Now, if you look down, you should see three vive trackers that should follow your body, and you should be ready to play!
 
The other settings on the window:
  
- Pause/Unpause tracking: Pause detection, if you want to freeze your fbt in place when sitting down.
- Smoothing window: The smoothing window in seconds. The higher it is, the smoother will motion be, but with more latency and more "wobblyness". Good values are 0.3 for speed, 0.5 for balanced and 0.7 for smoothness. You may also want to disable it and only use the next option.
- Additional smoothing: A diffrent kind of smoothing, from 0 to 1. Enabling this will reduce jitter and wobblyness by a lot, but also increases latency. A good value is 0.5 for speed, 0.7 for balance, and 0.9 for smoothness.
- Camera latency: The latency of your camera. Increase to reduce delay, but at the cost of more shakyness. Note that it will not work when smoothing window is disabled. Should probably never be larger than 0.1.
- Image rotation: Rotate the image to ensure it is upright, and mirror it if the camera feed is mirrored.
- Log frametimes to console: Dump the detection speed to console, for debug reasons.
  
The window also contains sliders for manual calibration of values. If automatic calibration doesnt allign the skeleton well enough, you can refine it manualy using the sliders and buttons.

Your controllers may dissapear or no longer work when you use it the first time. If that happens, restart steamvr.
  
Automatic scale calibration may not work for some people, mostly on lighthouse tracked headsets. If you notice your feet are far above the ground, disable automatic scale calibration and use the slider instead.
  
### Advanced settings
  
**NOTE:** Advanced settings will give you access to all settings, but plenty of them are still best at default, and may break detection otherwise! Read what they do below carefully!
  
When you get used to the software a bit and get it working well on normal mode, you can enable advanced mode to get access to a few new options, to further finetune it. It adds options to both the init settings and runtime settings:
  
New init settings:

- Maximum image size: The image size is limited to this value, even if the cameras resolution is greater, to reduce processing costs. Mediapipe runs on very low res anyway, so no need to change this. Will also make the camera window larger.
  
Some DEV options, that you probably dont want to use:
  - Preview skeleton in VR: Instead of spawning just three trackers for legs, the entire skeleton will be spawned and shown 2 meters in front of you. Useful for visualizing how well it works. Dont use for actual gameplay!
  - Spawn trackers for hands: Try to emulate controllers by spawning trackers for your hands. Works pretty bad, so I would recommend against using this.
  
MediaPipe estimator parameters:
  - The only one you really want to change here is Model complexity. If you have a very slow PC, you can set it to 0 to speed it up a bit at a reduction of accuracy. On the other side, if you have a beast CPU, you can try to set it to 2 for increased accuracy. 1 seems to be the best balance, however, so you probably want to stick to that.
  - Other parameters are described here: https://google.github.io/mediapipe/solutions/pose.html
  
New runtime settings:
  - The smoothing parameters now have two values, that you can switch between. Useful to if you want to have two profiles, one for sitting that has more agressive smoothing, and one for movement, that has less smoothing.
  - HMD to neck offset: This is the offset from the hmd to the base of your neck, that is necessary to align the mediapipe skeleton to the hmd. First value is left/right, second is up/down, third is forward/back. Default is 0.2 meters down, 0.1 meter back and should work well enough. If tilting your head side to side or looking up and down moves your legs, it is set incorrectly. Check Troubleshooting to fix it.
  
## Troubleshooting
    
**The app crashes with an ImportError: DLL load failed:**
 
This seems to be a problem with some windows "N" versions, which seem to miss some media features: Installing the media feature pack should fix it. Read more about it here: https://stackoverflow.com/a/54321350
  
**The camera doesn't open:**

For USB webcams:
  - Try a few diffrent IDs, 0, 1, 2 etc... If you have many virtual cameras installed, the number can go up to 10!
  - Check that the camera works in other apps, such as Discord
  - Check that the camera isnt opened in any other apps while trying to use it for MediaPipePose
  - Set the camera width and height to the resolution of the camera
  - Plug the camera into another USB port
  - Check/uncheck Attempt to open camera settings and try all the IDs again
  
For IP Webcam:
  - Ensure that the stream works when accessing it from the browser (just input the IP into the adress field of a web browser, it should connect to the stream)
  - Ensure that your phone is using WiFi and is on the same network as the PC. (the pc can be connected through ethernet, as long as its to the same router)
  - Check for typos. Its really easy to miss a number or a letter somewhere.
    
**Connection to SteamVR fails after 10 retries:**
  
  - Make sure SteamVR is open and a headset is connected
  - Make sure that you installed the driver with /driver_files/install_driver.exe, and that the driver installed properly
  - Open SteamVR settings -> startup -> addons, and make sure that apriltagtrackers is enabled
  - If SteamVR runs in administrator mode, you may have to run mediapipepose by running /bin/mediapipepose.exe as administrator
  - If using for VRChat, you can also just use OSC instead
  
**The tracking is unuseably bad:**
  
While the tracking is not perfect even under ideal conditions due to no depth information, there is still a few things you can do to improve it:
  
- Make sure that your entire body is seen on the camera, including your head!
- Make sure there is enough light in the room. and there shouldnt be any light sources behind you, such as any bright windows. Try to get as much lighting as you can from the direction of the camera.
- Mind what you wear: you need to be in contrast with the background, so dont wear clothes the same color as the background and avoid clothes with patterns.
- Play with the smoothing and latency parameters a bit. To learn what exactly they do, we have some nice graphs [here](https://github.com/ju1ce/April-Tag-VR-FullBody-Tracker/wiki/Refining-parameters).
 
**Looking up/down moves my avatar up/down, or tilting head left/right moves my avatar left/right:**
  
To fix this, you will have to finetune HMD to neck offset. It is only available when advanced mode is on, and is on the runtime GUI. The first value is x position(left/right, you want to keep this at 0), second is y (up/down) and third is z(forward/backwars). To correct this, follow the steps below:
  
Tilt your head to the left, then to the right, and observe what happens to the avatar. If your avatar moves with you, the y value is too high, and you want to reduce it (from -0.2 to -0.22 or so). If the avatar moves in the oposite direction from you it is too low, and you want to increase it (from -0.2 to -0.18 or so). Do this in small steps until your body no longer moves.
  
Now look up/down. If the avatar moves with you, the z value is too low, and you want to increase it (from 0.1 to 0.12 or so). If it moves the oposite, the z value is too high, and you want to decrease it (from 0.1 to 0.08 or so). Again, repeat in small steps until your avatar no longer moves with you!

  
**All the trackers are 2 meters away from me:**
  
The DEV: Preview skeleton in VR option will do this in order to preview the tracking, sort of like a mirror. This makes the tracking unusable for games though, so disable this option. And restart SteamVR after doing so.
  
**The trackers are way too high:**
  
If the trackers are far off the ground, or even above you, height calibration seems to have failed. Try to disable automatic scale calibration. This should enable a new slider to calibrate your height manualy.
  
**Trackers dont allign with my body:**
  
For automatic calibration, make sure that you stand straight and look straight ahead or some parts may not be calibrated well enough. If automatic calibration just doesnt seem to work, you can also use the sliders to calibrate it manualy. Rotation y will rotate your body around the up axis, rotation x will tilt you forward/backward, and rotation z will tilt you left/right. Adjust the values until the trackers align with your body!
  
**Trackers don't show up in VR, status window says "Move to wake up trackers"**
  
Problems with trackers may appear when using Additional Smoothing. Try disabling it.
  
This problem should now be fixed. If it still occurs, please let us know either by opening an issue or through the discord!
  
**In vrchat, both legs stick together**
  
First, make sure that the trackers align with the avatar properly. If they don't, you may need to recalibrate. On some avatars, you may also have to stand with your legs further apart to prevent this.

**In vrchat, trackers dont work and cause issues**

If there are any weird issues inside vrchat and nothing else works, it is usualy caused by mods. Mods can affect full body tracking systems in weird ways, even if the mod doesnt have anything to do with tracking. Try to uninstall all mods, even if they seem irrelevant.

Alternatively, you can also use the --no-mods vrchat launch option.
  
## Other tips:
  
- A wider FOV can help you have more room to move around, and ensure you can stand closer to the camera. If your camera/phone supports that, make sure to use it!

# MediaPipe version 

Thanks to John_ on the ApriltagTrackers discord, who reminded me that MediaPipe pose does in fact have 3d positions as well, the script was modified to use that version. It seems to be faster, pretty accurate, and should be easier to setup. Beside not needing the 3d model, the instructions on how to use are the same.

The movenet version has now been removed from the repo.


## Information for devs:
  
Any needed libraries are listed in install_libraries.bat. The mediapipepose.bat should run through a local python installation, but it seems broken right now, so just use a global installation of python 3.9.

