print("Importing libraries...")

import os
import sys

sys.path.append(os.getcwd())    #embedable python doesnt find local modules without this line

import time
import threading
import cv2
import numpy as np
from helpers import mediapipeTo3dpose, get_rot_mediapipe, get_rot_hands, keypoints_to_original, normalize_screen_coordinates, get_rot, sendToSteamVR
from scipy.spatial.transform import Rotation as R

import inference_gui
import parameters

import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

use_steamvr = True

print("Reading parameters...")

params = parameters.Parameters()
if params.exit_ready:
    print("Exiting... You can close the window after 10 seconds.")
    exit(0)

print("Opening camera...")

image_from_thread = None
image_ready = False

def camera_thread_fun(params):
    #A seperate camera thread that captures images and saves it to a variable to be read by the main program.
    #Mostly used to free the main thread from image decoding overhead and to ensure frames are just skipped if detection is slower than camera fps
    global cameraid, image_from_thread, image_ready
    
    if len(params.cameraid) <= 2:
        cameraid = int(params.cameraid)
        if params.camera_settings:
            cap = cv2.VideoCapture(cameraid, 700)
            cap.set(cv2.CAP_PROP_SETTINGS,1)
        else:
            cap = cv2.VideoCapture(cameraid)   
    else:
        cameraid = params.cameraid
        cap = cv2.VideoCapture(cameraid)  
    
    #codec = 0x47504A4D
    #cap.set(cv2.CAP_PROP_FOURCC, codec)
    
    if params.camera_height != 0:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(params.camera_height))
        
    if params.camera_width != 0:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(params.camera_width))
        
    print("Camera opened!")
    while True:
        ret, image_from_thread = cap.read()    

        image_ready = True
        
        if ret == 0:
            print("[ERROR]Camera capture failed! Check the CameraID parameter.")
            params.exit_ready = True
            return


def shutdown(params):
    # first save parameters 
    print("Saving parameters...")
    params.save_params()

    cv2.destroyAllWindows()
    print("Exiting... You can close the window after 10 seconds.")
    exit(0)


camera_thread = threading.Thread(target=camera_thread_fun, args=(params,), daemon=True)
camera_thread.start()      #start our thread, which starts camera capture

gui_thread = threading.Thread(target=inference_gui.make_inference_gui, args=(params,), daemon=True)
gui_thread.start()

if use_steamvr:
    print("Connecting to SteamVR")
    
    #ask the driver, how many devices are connected to ensure we dont add additional trackers 
    #in case we restart the program
    numtrackers = sendToSteamVR("numtrackers")
    if numtrackers is None:
        print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
        shutdown(params)
        
    numtrackers = int(numtrackers[2])
 
#games use 3 trackers, but we can also send the entire skeleton if we want to look at how it works
totaltrackers = 23 if params.preview_skeleton else  3
if params.use_hands:
    totaltrackers = 5
if params.ignore_hip:
    totaltrackers -= 1

roles = ["TrackerRole_Waist", "TrackerRole_RightFoot", "TrackerRole_LeftFoot"]

if params.ignore_hip and not params.preview_skeleton:
    del roles[0]

if params.use_hands:
    roles.append("TrackerRole_Handed")
    roles.append("TrackerRole_Handed")

for i in range(len(roles),totaltrackers):
    roles.append("None")

if use_steamvr:
    for i in range(numtrackers,totaltrackers):
        #sending addtracker to our driver will... add a tracker. to our driver.
        resp = sendToSteamVR(f"addtracker MediaPipeTracker{i} {roles[i]}", wait_time=0.2)
        if resp is None:
            print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
            shutdown(params)
    
    resp = sendToSteamVR(f"settings 50 {params.smoothing} {params.additional_smoothing}")
    if resp is None:
        print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
        shutdown(params)

print("Starting pose detector...")

pose = mp_pose.Pose(                #create our detector. These are default parameters as used in the tutorial. 
    model_complexity=params.model,
    min_detection_confidence=0.5,
    min_tracking_confidence=params.min_tracking_confidence,
    smooth_landmarks=params.smooth_landmarks,
    static_image_mode=params.static_image) 

cv2.namedWindow("out")

#Main program loop:

rotation = 0
i = 0

prev_smoothing = params.smoothing
prev_add_smoothing = params.additional_smoothing

while(True):
    # Capture frame-by-frame
    if params.exit_ready:
        shutdown(params)
        
    if prev_smoothing != params.smoothing or prev_add_smoothing != params.additional_smoothing:
        print(f"Changed smoothing value from {prev_smoothing} to {params.smoothing}")
        print(f"Changed additional smoothing from {prev_add_smoothing} to {params.additional_smoothing}")
        
        prev_smoothing = params.smoothing
        prev_add_smoothing = params.additional_smoothing

        if use_steamvr:
            resp = sendToSteamVR(f"settings 50 {params.smoothing} {params.additional_smoothing}")
            if resp is None:
                print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
                shutdown(params)
    
    if not image_ready:     #wait untill camera thread captures another image
        time.sleep(0.001)
        continue

    img = image_from_thread.copy() #some may say I need a mutex here. I say this works fine.
    image_ready = False         
    
    if params.rotate_image is not None:        #if set, rotate the image
        img = cv2.rotate(img, params.rotate_image)
        
    if params.mirror:
        img = cv2.flip(img,1)

    if max(img.shape) > params.maximgsize:         #if set, ensure image does not exceed the given size.
        ratio = max(img.shape)/params.maximgsize
        img = cv2.resize(img,(int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
    
    if params.paused:
        cv2.imshow("out",img)
        cv2.waitKey(1)
        continue
    
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    #print(image.shape)
    
    t0 = time.time()
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.    copied from the tutorial
    img.flags.writeable = False
    results = pose.process(img)
    img.flags.writeable = True

    if results.pose_world_landmarks:        #if any pose was detected
        
        pose3d = mediapipeTo3dpose(results.pose_world_landmarks.landmark)   #convert keypoints to a format we use
        
        pose3d[:,0] = -pose3d[:,0]      #flip the points a bit since steamvrs coordinate system is a bit diffrent
        pose3d[:,1] = -pose3d[:,1]

        pose3d_og = pose3d.copy()
        params.pose3d_og = pose3d_og
        
        for j in range(pose3d.shape[0]):        #apply the rotations from the sliders
            pose3d[j] = params.global_rot_z.apply(pose3d[j])
            pose3d[j] = params.global_rot_x.apply(pose3d[j])
            pose3d[j] = params.global_rot_y.apply(pose3d[j])
        
        if not params.feet_rotation:
            rots = get_rot(pose3d)          #get rotation data of feet and hips from the position-only skeleton data
        else:
            rots = get_rot_mediapipe(pose3d)
            
        if params.use_hands:
            hand_rots = get_rot_hands(pose3d)
        
        if use_steamvr:
            array = sendToSteamVR("getdevicepose 0")        #get hmd data to allign our skeleton to
            if array is None:
                print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
                shutdown(params)

            #if "error" in array:    #continue to next iteration if there is an error
            #    continue
            try:
                headsetpos = [float(array[3]),float(array[4]),float(array[5])]
            except:
                print(f"no error but this:")
                print(array)
            headsetrot = R.from_quat([float(array[7]),float(array[8]),float(array[9]),float(array[6])])
            
            neckoffset = headsetrot.apply(params.hmd_to_neck_offset)   #the neck position seems to be the best point to allign to, as its well defined on 
                                                                #the skeleton (unlike the eyes/nose, which jump around) and can be calculated from hmd.   

            if params.recalibrate:
                print("frame to recalibrate")
                
            else:
                pose3d = pose3d * params.posescale     #rescale skeleton to calibrated height
                #print(pose3d)
                offset = pose3d[7] - (headsetpos+neckoffset)    #calculate the position of the skeleton
                if not params.preview_skeleton:
                    numadded = 3
                    if not params.ignore_hip:
                        for i in [(0,1),(5,2),(6,0)]:
                            joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                            if use_steamvr:
                                resp = sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} {params.camera_latency} 0.8") 
                                if resp is None:
                                    print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
                                    shutdown(params)
                    else:
                        for i in [(0,1),(5,2)]:
                            joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                            if use_steamvr:
                                resp = sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} {params.camera_latency} 0.8") 
                                if resp is None:
                                    print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
                                    shutdown(params)
                            numadded = 2
                    if params.use_hands:
                        for i in [(10,0),(15,1)]:
                            joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                            if use_steamvr:
                                resp = sendToSteamVR(f"updatepose {i[1]+numadded} {joint[0]} {joint[1]} {joint[2]} {hand_rots[i[1]][3]} {hand_rots[i[1]][0]} {hand_rots[i[1]][1]} {hand_rots[i[1]][2]} {params.camera_latency} 0.8") 
                                if resp is None:
                                    print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
                                    shutdown(params)
                    
                else:
                    for i in range(23):
                        joint = pose3d[i] - offset      #if previewing skeleton, send the position of each keypoint to steamvr without rotation
                        if use_steamvr:
                            resp = sendToSteamVR(f"updatepose {i} {joint[0]} {joint[1]} {joint[2] - 2} 1 0 0 0 {params.camera_latency} 0.8") 
                            if resp is None:
                                print("[ERROR]Could not connect to SteamVR after 10 tries! Launch SteamVR and try again.")
                                shutdown(params)
    
    
    #print(f"Inference time: {time.time()-t0}\nSmoothing value: {smoothing}\n")        #print how long it took to detect and calculate everything
    inference_time = time.time() - t0
    
    if params.log_frametime:
        print(f"Inference time: {inference_time}")
    
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)       #convert back to bgr and draw the pose
    mp_drawing.draw_landmarks(
        img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    img = cv2.putText(img, f"{inference_time:1.3f}, FPS:{int(1/inference_time)}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
    
    cv2.imshow("out",img)           #show image, exit program if we press esc
    if cv2.waitKey(1) == 27:
        #print("Exiting... You can close the window after 10 seconds.")
        #exit(0)
        shutdown()
