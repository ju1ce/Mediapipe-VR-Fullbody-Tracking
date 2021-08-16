print("Importing libraries....")

import os
import sys

sys.path.append(os.getcwd())    #embedable python doesnt find local modules without this line

import time
import threading
import cv2
import numpy as np
from helpers import draw_pose, keypoints_to_original, normalize_screen_coordinates, get_rot
from scipy.spatial.transform import Rotation as R
from guitest import getparams

def mediapipeTo3dpose(lms):
    
    #convert landmarks returned by mediapipe to skeleton that I use.
    #lms = results.pose_world_landmarks.landmark
    
    pose = np.zeros((17,3))

    pose[0]=[lms[28].x,lms[28].y,lms[28].z]
    pose[1]=[lms[26].x,lms[26].y,lms[26].z]
    pose[2]=[lms[24].x,lms[24].y,lms[24].z]
    pose[3]=[lms[23].x,lms[23].y,lms[23].z]
    pose[4]=[lms[25].x,lms[25].y,lms[25].z]
    pose[5]=[lms[27].x,lms[27].y,lms[27].z]

    pose[6]=[0,0,0]

    #some keypoints in mediapipe are missing, so we calculate them as avarage of two keypoints
    pose[7]=[lms[12].x/2+lms[11].x/2,lms[12].y/2+lms[11].y/2,lms[12].z/2+lms[11].z/2]
    pose[8]=[lms[10].x/2+lms[9].x/2,lms[10].y/2+lms[9].y/2,lms[10].z/2+lms[9].z/2]

    pose[9]=[lms[0].x,lms[0].y,lms[0].z]

    pose[10]=[lms[15].x,lms[15].y,lms[15].z]
    pose[11]=[lms[13].x,lms[13].y,lms[13].z]
    pose[12]=[lms[11].x,lms[11].y,lms[11].z]

    pose[13]=[lms[12].x,lms[12].y,lms[12].z]
    pose[14]=[lms[14].x,lms[14].y,lms[14].z]
    pose[15]=[lms[16].x,lms[16].y,lms[16].z]

    pose[16]=[pose[6][0]/2+pose[7][0]/2,pose[6][1]/2+pose[7][1]/2,pose[6][2]/2+pose[7][2]/2]

    return pose

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
totaltrackers = 17 if preview_skeleton else 3

roles = ["TrackerRole_Waist", "TrackerRole_LeftFoot", "TrackerRole_RightFoot"]

for i in range(numtrackers,totaltrackers):
    #sending addtracker to our driver will... add a tracker. to our driver.
    resp = sendToSteamVR(f"addtracker MediaPipeTracker{i} {roles[i]}")
    while "error" in resp:
        resp = sendToSteamVR(f"addtracker MediaPipeTracker{i} {roles[i]}")
        print(resp)
        time.sleep(0.2)
    time.sleep(0.2)
    
resp = sendToSteamVR("settings 50 0.5")
while "error" in resp:
    resp = sendToSteamVR("settings 50 0.5")
    print(resp)
    time.sleep(1)


print("Starting pose detector...")

pose = mp_pose.Pose(                #create our detector. These are default parameters as used in the tutorial. 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=1)

print("Waiting for you to put on your headset...")

prevhead = None
while True:
    #This loop tries to detect when you put your headset on.
    #It querries steamvr for the headset position each second, then check whether its height
    #changed for more than 10cm from the starting position. If yes, we assumethe headset is in use.
    
    array = sendToSteamVR("getdevicepose 0")
    while "error" in array:
        print("Failed to get HMD pose from SteamVR! Retrying...")
        time.sleep(1)
        array = sendToSteamVR("getdevicepose 0")  
    
    headsetpos = float(array[4])
    if prevhead is None:
        prevhead = headsetpos
    elif abs(prevhead-headsetpos) > 0.1 or dont_wait_hmd:
        print("Headset detected!")
        break
    time.sleep(1)
    
for i in range(5):
    #just wait for 5 seconds to ensure the user is in place, so height will be calibrated properly
    print(f"Calibration will start in {5-i}")
    time.sleep(1)
   
global_rot_y = R.from_euler('y',0,degrees=True)     #default rotations, for 0 degrees around y and x
global_rot_x = R.from_euler('x',0,degrees=True) 
def rot_change_y(value):
    global global_rot_y                                     #callback functions. Whenever the value on sliders are changed, they are called
    global_rot_y = R.from_euler('y',value,degrees=True)     #and the rotation is updated with the new value.
    
def rot_change_x(value):
    global global_rot_x
    global_rot_x = R.from_euler('x',value,degrees=True) 
    
cv2.namedWindow("out")
cv2.createTrackbar("rotation_y","out",0,360,rot_change_y)   #Create rotation sliders and assign callback functions
cv2.createTrackbar("rotation_x","out",0,360,rot_change_x)
  
#Main program loop:

recalibrate = True  
posescale = 1
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

        
        for j in range(pose3d.shape[0]):        #apply the rotations from the sliders
            pose3d[j] = global_rot_x.apply(pose3d[j])
            pose3d[j] = global_rot_y.apply(pose3d[j])
        
        rots = get_rot(pose3d)          #get rotation data of feet and hips from the position-only skeleton data
        
        array = sendToSteamVR("getdevicepose 0")        #get hmd data to allign our skeleton to

        if "error" not in array:
            headsetpos = [float(array[3]),float(array[4]),float(array[5])]
            headsetrot = R.from_quat([float(array[7]),float(array[8]),float(array[9]),float(array[6])])
            
            neckoffset = headsetrot.apply(hmd_to_neck_offset)   #the neck position seems to be the best point to allign to, as its well defined on 
                                                                #the skeleton (unlike the eyes/nose, which jump around) and can be calculated from hmd.
            
            if recalibrate:
                #calculate the height of the skeleton, calculate the height in steamvr as distance of hmd from the ground.
                #divide the two to get scale 
                skelSize = np.max(pose3d, axis=0)-np.min(pose3d, axis=0)+0.2
                posescale = headsetpos[1]/skelSize[1]
                recalibrate = False
            else:
                pose3d = pose3d * posescale     #rescale skeleton to calibrated height
                #print(pose3d)
                offset = pose3d[7] - (headsetpos+neckoffset)    #calculate the position of the skeleton
                if not preview_skeleton:
                    for i in [(0,1),(5,2),(6,0)]:
                        joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                        sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} 0.05 0.8") 
                else:
                    for i in range(17):
                        joint = pose3d[i] - offset      #if previewing skeleton, send the position of each keypoint to steamvr without rotation
                        sendToSteamVR(f"updatepose {i} {joint[0]} {joint[1]} {joint[2]-2} 1 0 0 0 0.05 0.8") 

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











