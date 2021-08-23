print("Importing libraries....")

import os
import sys

sys.path.append(os.getcwd())    #embedable python doesnt find local modules without this line

import time
import threading
import cv2
import numpy as np
from helpers import mediapipeTo3dpose, get_rot_mediapipe,draw_pose, keypoints_to_original, normalize_screen_coordinates, get_rot
from scipy.spatial.transform import Rotation as R
from guitest import getparams

import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

print("Reading parameters...")

param = getparams()

#PARAMETERS:
#model =  1          #TODO: add parameter for which model size to use
maximgsize = param["imgsize"]               #to prevent working with huge images, images that have one axis larger than this value will be downscaled.
cameraid = param["camid"]                    #to use with an usb or virtual webcam. If 0 doesnt work/opens wrong camera, try numbers 1-5 or so
#cameraid = "http://192.168.1.102:8080/video"   #to use ip webcam, uncomment this line and change to your ip
hmd_to_neck_offset = param["neckoffset"]    #offset of your hmd to the base of your neck, to ensure the tracking is stable even if you look around. Default is 20cm down, 10cm back.
preview_skeleton = param["prevskel"]             #if True, whole skeleton will appear in vr 2 meters in front of you. Good to visualize if everything is working
dont_wait_hmd = param["waithmd"]                  #dont wait for movement from hmd, start inference immediately.
rotate_image = param["rotate"] # cv2.ROTATE_90_CLOCKWISE # cv2.ROTATE_90_COUTERCLOCKWISE # cv2.ROTATE_180 # None # if you want, rotate the camera
camera_latency = param["camlatency"]
smoothing = param["smooth"]
feet_rotation = param["feetrot"]
calib_scale = param["calib_scale"]
calib_tilt = param["calib_tilt"]

print("Opening camera...")

image_from_thread = None
image_ready = False

def camera_thread():
    #A seperate camera thread that captures images and saves it to a variable to be read by the main program.
    #Mostly used to free the main thread from image decoding overhead and to ensure frames are just skipped if detection is slower than camera fps
    global cameraid, image_from_thread, image_ready
    
    if len(cameraid) <= 2:
        cameraid = int(cameraid)
    
    cap = cv2.VideoCapture(cameraid)
    print("Camera opened!")
    while True:
        ret, image_from_thread = cap.read()    

        image_ready = True
        
        assert ret, "Camera capture failed! Check the cameraid parameter."

thread = threading.Thread(target=camera_thread, daemon=True)
thread.start()      #start our thread, which starts camera capture

def sendToSteamVR(text):
    #Function to send a string to my steamvr driver through a named pipe.
    #open pipe -> send string -> read string -> close pipe
    #sometimes, something along that pipeline fails for no reason, which is why the try catch is needed.
    #returns an array containing the values returned by the driver.
    try:
        pipe = open(r'\\.\pipe\ApriltagPipeIn', 'rb+', buffering=0)
        some_data = str.encode(text)
        pipe.write(some_data)
        resp = pipe.read(1024)
    except:
        return ["error"]
    string = resp.decode("utf-8")
    array = string.split(" ")
    pipe.close()
    
    return array
 
print("Connecting to SteamVR")
 
#ask the driver, how many devices are connected to ensure we dont add additional trackers 
#in case we restart the program
numtrackers = sendToSteamVR("numtrackers")
for i in range(10):
    if "error" in numtrackers:
        print("Error in SteamVR connection. Retrying...")
        time.sleep(1)
        numtrackers = sendToSteamVR("numtrackers")
    else:
        break
        
if "error" in numtrackers:
    print("Could not connect to SteamVR after 10 retries!")
    time.sleep(10)
    assert 0, "Could not connect to SteamVR after 10 retries"
 
numtrackers = int(numtrackers[2])
 
#games use 3 trackers, but we can also send the entire skeleton if we want to look at how it works
totaltrackers = 23 if preview_skeleton else 3

roles = ["TrackerRole_Waist", "TrackerRole_RightFoot", "TrackerRole_LeftFoot"]

for i in range(len(roles),totaltrackers):
    roles.append("None")

for i in range(numtrackers,totaltrackers):
    #sending addtracker to our driver will... add a tracker. to our driver.
    resp = sendToSteamVR(f"addtracker MediaPipeTracker{i} {roles[i]}")
    while "error" in resp:
        resp = sendToSteamVR(f"addtracker MediaPipeTracker{i} {roles[i]}")
        print(resp)
        time.sleep(0.2)
    time.sleep(0.2)
    
resp = sendToSteamVR(f"settings 50 {smoothing}")
while "error" in resp:
    resp = sendToSteamVR(f"settings 50 {smoothing}")
    print(resp)
    time.sleep(1)


print("Starting pose detector...")

pose = mp_pose.Pose(                #create our detector. These are default parameters as used in the tutorial. 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=1) 
  
global_rot_y = R.from_euler('y',0,degrees=True)     #default rotations, for 0 degrees around y and x
global_rot_x = R.from_euler('x',0,degrees=True) 
global_rot_z = R.from_euler('z',0,degrees=True) 
def rot_change_y(value):
    global global_rot_y                                     #callback functions. Whenever the value on sliders are changed, they are called
    global_rot_y = R.from_euler('y',value,degrees=True)     #and the rotation is updated with the new value.
    
def rot_change_x(value):
    global global_rot_x
    global_rot_x = R.from_euler('x',value-90,degrees=True) 
    
def rot_change_z(value):
    global global_rot_z
    global_rot_z = R.from_euler('z',value-180,degrees=True) 
  
recalibrate = False 
def change_recalibrate(value):
    global recalibrate 
    if value == 1:
        recalibrate = True
    else:
        recalibrate = False
       
posescale = 1       
def change_scale(value):
    global posescale
    posescale = value/50 + 0.5
    
cv2.namedWindow("out")
cv2.createTrackbar("rotation_y","out",0,360,rot_change_y)   #Create rotation sliders and assign callback functions
if not calib_tilt:
    cv2.createTrackbar("rotation_x","out",90,180,rot_change_x)
    cv2.createTrackbar("rotation_z","out",180,360,rot_change_z)
if not calib_scale:
    cv2.createTrackbar("scale","out",25,100,change_scale)
if calib_scale or calib_tilt:
    cv2.createTrackbar("recalib","out",0,1,change_recalibrate)
  
#Main program loop:

rotation = 0

i = 0
while(True):
    # Capture frame-by-frame
    
    if not image_ready:     #wait untill camera thread captures another image
        time.sleep(0.001)
        continue

    img = image_from_thread.copy() #some may say I need a mutex here. I say this works fine.
    image_ready = False         
    
    if rotate_image is not None:        #if set, rotate the image
        img = cv2.rotate(img, rotate_image)

    if max(img.shape) > maximgsize:         #if set, ensure image does not exceed the given size.
        ratio = max(img.shape)/maximgsize
        img = cv2.resize(img,(int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
    
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
        
        for j in range(pose3d.shape[0]):        #apply the rotations from the sliders
            pose3d[j] = global_rot_z.apply(pose3d[j])
            pose3d[j] = global_rot_x.apply(pose3d[j])
            pose3d[j] = global_rot_y.apply(pose3d[j])
        
        if not feet_rotation:
            rots = get_rot(pose3d)          #get rotation data of feet and hips from the position-only skeleton data
        else:
            rots = get_rot_mediapipe(pose3d)
        
        array = sendToSteamVR("getdevicepose 0")        #get hmd data to allign our skeleton to

        if "error" not in array:
            headsetpos = [float(array[3]),float(array[4]),float(array[5])]
            headsetrot = R.from_quat([float(array[7]),float(array[8]),float(array[9]),float(array[6])])
            
            neckoffset = headsetrot.apply(hmd_to_neck_offset)   #the neck position seems to be the best point to allign to, as its well defined on 
                                                                #the skeleton (unlike the eyes/nose, which jump around) and can be calculated from hmd.
            
            if recalibrate:
            
                if calib_tilt:
                    feet_middle = (pose3d_og[0] + pose3d_og[5])/2
                
                    ## roll calibaration
                    
                    value = np.arctan2(feet_middle[0],-feet_middle[1])
                    
                    print("Precalib z angle: ", value * 57.295779513)
                    
                    global_rot_z = R.from_euler('z',-value)
                    
                    for j in range(pose3d_og.shape[0]):
                        pose3d_og[j] = global_rot_z.apply(pose3d_og[j])
                        
                    feet_middle = (pose3d_og[0] + pose3d_og[5])/2
                    value = np.arctan2(feet_middle[0],-feet_middle[1])
                    
                    print("Postcalib z angle: ", value * 57.295779513)
                     
                    ##tilt calibration
                     
                    
                    value = np.arctan2(feet_middle[2],-feet_middle[1])
                    
                    print("Precalib x angle: ", value * 57.295779513)
                    
                    global_rot_x = R.from_euler('x',value)
                
                    for j in range(pose3d_og.shape[0]):
                        pose3d_og[j] = global_rot_x.apply(pose3d_og[j])
                        
                    feet_middle = (pose3d_og[0] + pose3d_og[5])/2
                    value = np.arctan2(feet_middle[2],-feet_middle[1])
                    
                    print("Postcalib x angle: ", value * 57.295779513)
                
                if calib_scale:
                    #calculate the height of the skeleton, calculate the height in steamvr as distance of hmd from the ground.
                    #divide the two to get scale 
                    skelSize = np.max(pose3d_og, axis=0)-np.min(pose3d_og, axis=0)
                    posescale = headsetpos[1]/skelSize[1]
                recalibrate = False
                
            else:
                pose3d = pose3d * posescale     #rescale skeleton to calibrated height
                #print(pose3d)
                offset = pose3d[7] - (headsetpos+neckoffset)    #calculate the position of the skeleton
                if not preview_skeleton:
                    for i in [(0,1),(5,2),(6,0)]:
                        joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                        sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} {camera_latency} 0.8") 
                else:
                    for i in range(23):
                        joint = pose3d[i] - offset      #if previewing skeleton, send the position of each keypoint to steamvr without rotation
                        sendToSteamVR(f"updatepose {i} {joint[0]} {joint[1]} {joint[2] - 2} 1 0 0 0 {camera_latency} 0.8") 

    print("inference time:", time.time()-t0)        #print how long it took to detect and calculate everything


    #cv2.imshow("out",image)
    #cv2.waitKey(0)
    
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)       #convert back to bgr and draw the pose
    mp_drawing.draw_landmarks(
        img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    cv2.imshow("out",img)           #show image, exit program if we press esc
    if cv2.waitKey(1) == 27:
        print("Exiting... You can close the window after 10 seconds.")
        exit(0)











