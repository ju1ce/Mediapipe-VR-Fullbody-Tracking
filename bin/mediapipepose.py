print("Importing libraries...")

import os
import sys

sys.path.append(os.getcwd())    #embedable python doesnt find local modules without this line

import time
import threading
import cv2
import numpy as np

from helpers import  CameraStream, shutdown, mediapipeTo3dpose, get_rot_mediapipe, get_rot_hands, draw_pose, keypoints_to_original, normalize_screen_coordinates, get_rot
from scipy.spatial.transform import Rotation as R
from backends import DummyBackend, SteamVRBackend, VRChatOSCBackend
import webui

import inference_gui
import parameters

import tkinter as tk

import mediapipe as mp


def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    use_steamvr = True
    
    print("INFO: Reading parameters...")

    params = parameters.Parameters()
    
    if params.webui:
        webui_thread = threading.Thread(target=webui.start_webui, args=(params,), daemon=True)
        webui_thread.start()
    else:
        print("INFO: WebUI disabled in parameters")

    backends = { 0: DummyBackend, 1: SteamVRBackend, 2: VRChatOSCBackend }
    backend = backends[params.backend]()
    backend.connect(params)

    if params.exit_ready:
        sys.exit("INFO: Exiting... You can close the window after 10 seconds.")

    print("INFO: Opening camera...")

    camera_thread = CameraStream(params)

    #making gui
    gui_thread = threading.Thread(target=inference_gui.make_inference_gui, args=(params,), daemon=True)
    gui_thread.start()

    print("INFO: Starting pose detector...")

    #create our detector. These are default parameters as used in the tutorial. 
    pose = mp_pose.Pose(model_complexity=params.model, 
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

    while True:
        # Capture frame-by-frame
        if params.exit_ready:
            shutdown(params)
            
        if prev_smoothing != params.smoothing or prev_add_smoothing != params.additional_smoothing:
            print(f"INFO: Changed smoothing value from {prev_smoothing} to {params.smoothing}")
            print(f"INFO: Changed additional smoothing from {prev_add_smoothing} to {params.additional_smoothing}")

            prev_smoothing = params.smoothing
            prev_add_smoothing = params.additional_smoothing

            backend.onparamchanged(params)

        #wait untill camera thread captures another image
        if not camera_thread.image_ready:     
            time.sleep(0.001)
            continue

        #some may say I need a mutex here. I say this works fine.
        img = camera_thread.image_from_thread.copy() 
        camera_thread.image_ready = False         
        
        #if set, rotate the image
        if params.rotate_image is not None:       
            img = cv2.rotate(img, params.rotate_image)
            
        if params.mirror:
            img = cv2.flip(img,1)

        #if set, ensure image does not exceed the given size.
        if max(img.shape) > params.maximgsize:        
            ratio = max(img.shape)/params.maximgsize
            img = cv2.resize(img, (int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
        
        if params.paused:
            cv2.imshow("out", img)
            cv2.waitKey(1)
            continue
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        #print(image.shape)
        
        t0 = time.time()
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.    copied from the tutorial
        img.flags.writeable = False
        results = pose.process(img)
        img.flags.writeable = True

        if results.pose_world_landmarks:        #if any pose was detected
            
            pose3d = mediapipeTo3dpose(results.pose_world_landmarks.landmark)   #convert keypoints to a format we use
            
            #do we need this with osc as well?
           
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
            else:
                hand_rots = None
                
            
            #pose3d[0] = [1,0,1]
            #rots = (rots[0], R.from_euler('ZXY',[i/17,i/11,i/10]).as_quat(),rots[2])   #for testing rotation conversions
            #i+=1
            
            if not backend.updatepose(params, pose3d, rots, hand_rots):
                continue
        
        
        #print(f"Inference time: {time.time()-t0}\nSmoothing value: {smoothing}\n")        #print how long it took to detect and calculate everything
        inference_time = time.time() - t0
        
        if params.log_frametime:
            print(f"INFO: Inference time: {inference_time}")
        
        img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)       #convert back to bgr and draw the pose
        mp_drawing.draw_landmarks(
            img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        img = cv2.putText(img, f"{inference_time:1.3f}, FPS:{int(1/inference_time)}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
        
        cv2.imshow("out", img)           #show image, exit program if we press esc
        if cv2.waitKey(1) == 27:
            backend.disconnect()
            shutdown(params)


if __name__ == "__main__":
    main()

