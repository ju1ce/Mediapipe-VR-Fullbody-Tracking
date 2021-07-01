print("Importing libraries....")

import os
import tensorflow as tf
import tensorflow_hub as hub
import time
from model import TemporalModelOptimized1f
import torch
import threading
import cv2
import numpy as np
from helpers import draw_pose, get_bbox, keypoints_to_original, normalize_screen_coordinates, get_rot
from scipy.spatial.transform import Rotation as R

print("Reading parameters...")

#PARAMETERS:
modelname = "thunder"           #thunder for accuracy, lightning for speed
maximgsize = 800                #to prevent working with huge images, images that have one axis larger than this value will be downscaled.
#cameraid = 0                    #to use with an usb or virtual webcam. If 0 doesnt work/opens wrong camera, try numbers 1-5 or so
cameraid = "http://192.168.1.105:8080/video"   #to use ip webcam, uncomment this line and change to your ip
num_of_threads = 16		#how many threads will the program run on.
hmd_to_neck_offset = [0,-0.20,0.20]    #offset of your hmd to the base of your neck, to ensure the tracking is stable even if you look around
preview_skeleton = False                #if True, whole skeleton will appear in vr 2 meters in front of you. Good to visualize if everything is working

assert (modelname in ["thunder","lightning"]), "Modelname must be thunder or lightning"

if modelname == "thunder":
    imgsize = 256	
elif modelname == "lightning":
    imgsize = 196	

# Download the model from TF Hub.

tf.config.threading.set_intra_op_parallelism_threads(num_of_threads)

movenet_path = f'bin\\movenet_model_{modelname}'

if not os.path.exists(movenet_path): 

    print("Loading 2d model from tensorflow hub...")   
    module = hub.load(f"https://tfhub.dev/google/movenet/singlepose/{modelname}/3")
    print(module.signatures['serving_default'])
    sig = module.signatures
    tf.saved_model.save(module, movenet_path, signatures=sig)

else:
    print(f'Loading 2d model from file...')
    module = tf.saved_model.load(movenet_path)

print("2d model loaded!")

model = module.signatures['serving_default']
#print(module.summary())

assert 0

def movenet(input_image):
    """Runs detection on an input image.

    Args:
      input_image: A [1, height, width, 3] tensor represents the input image
        pixels. Note that the height/width should already be resized and match the
        expected input resolution of the model before passing into this function.

    Returns:
      A [1, 1, 17, 3] float numpy array representing the predicted keypoint
      coordinates and scores.
    """
    model = module.signatures['serving_default']

    # SavedModel format expects tensor type of int32.
    input_image = tf.cast(input_image, dtype=tf.int32)
    # Run model inference.
    outputs = model(input_image)
    # Output is a [1, 1, 17, 3] tensor.
    keypoint_with_scores = outputs['output_0'].numpy()
    return keypoint_with_scores		

print("Loading 3d model from file...")

model_3d = TemporalModelOptimized1f(17,2,17,[3,3,3], causal=True)
checkpoint = torch.load("bin\checkpoint_3d_1024_0001_fullimg.pth", map_location=torch.device('cpu'))
model_3d.load_state_dict(checkpoint)
model_3d.eval()
model_3d.cpu()

print("3d model loaded!")

print("Opening camera...")

image_from_thread = None
image_ready = False

def camera_thread():
    global cameraid, image_from_thread, image_ready
    cap = cv2.VideoCapture(cameraid)
    print("Camera opened!")
    while True:
        ret, image_from_thread = cap.read()            

        image_ready = True
        assert ret, "Camera capture failed! Check the cameraid parameter."

thread = threading.Thread(target=camera_thread, daemon=True)
thread.start()

def sendToSteamVR(text):

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
 
numtrackers = int(sendToSteamVR("numtrackers")[2])

totaltrackers = 17 if preview_skeleton else 3

for i in range(numtrackers,totaltrackers):
    print(sendToSteamVR("addtracker"))
    time.sleep(0.2)

print("Waiting for you to put on your headset...")

prevhead = None

while True:
    array = sendToSteamVR("getdevicepose 0")  
    #print(array)
    
    headsetpos = float(array[4])
    #print(prevhead,headsetpos)
    if prevhead is None:
        prevhead = headsetpos
    elif abs(prevhead-headsetpos) > 0.1:
        print("Headset detected!")
        break
    time.sleep(1)
    
for i in range(5):
    print(f"Calibration will start in {5-i}")
    time.sleep(1)
   
global_rot_y = R.from_euler('y',0,degrees=True) 
global_rot_x = R.from_euler('x',0,degrees=True) 
def rot_change_y(value):
    global global_rot_y
    global_rot_y = R.from_euler('y',value,degrees=True) 
    
def rot_change_x(value):
    global global_rot_x
    global_rot_x = R.from_euler('x',value,degrees=True) 
    
cv2.namedWindow("out")
cv2.createTrackbar("rotation_y","out",0,360,rot_change_y)
cv2.createTrackbar("rotation_x","out",0,360,rot_change_x)

    
#Main program loop:

recalibrate = True
posescale = 2
rotation = 0

prevpose = None

i = 0
poses = []

while(True):
    # Capture frame-by-frame
    
    if not image_ready:
        time.sleep(0.001)
        continue
        
    #print("rotation:", rot_slider)

    img = image_from_thread.copy()
    image_ready = False

    if max(img.shape) > maximgsize:
        ratio = max(img.shape)/maximgsize
        img = cv2.resize(img,(int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
    
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    image = tf.convert_to_tensor(img)
    image = tf.expand_dims(image, axis=0)
    # Resize and pad the image to keep the aspect ratio and fit the expected size.
    
    if prevpose is None:
        center = [image.shape[1]/2,image.shape[2]/2]
        scale = max(image.shape[1],image.shape[2])
        image = tf.image.resize_with_pad(image, imgsize, imgsize)
    else:
        image, center, scale = get_bbox(image,prevpose,imgsize)

    #print(image.shape)
    
    t0 = time.time()
    # Run model inference.
    outputs = movenet(image)
    # Output is a [1, 1, 17, 3] tensor.
    
    pose = np.array(outputs[0][0])

    #calculate confidence in our pose as an avarage of keypoint confidences
    avgconf = np.mean(pose[:,2])
    
    pose = keypoints_to_original(scale,center,pose)
    
    #Lifting pose to 3d needs 27 past 2d poses
    if len(poses) < 27:
        poses.append(normalize_screen_coordinates(pose[:,[1, 0]],img.shape[1],img.shape[0]))
    else:
        poses.pop(0)
        poses.append(normalize_screen_coordinates(pose[:,[1, 0]],img.shape[1],img.shape[0]))
    
    if len(poses) >= 27:
        poses_in = np.array(poses)
        pose3d = model_3d(torch.from_numpy(poses_in.astype('float32')).unsqueeze(0).cpu())[0].cpu().detach().numpy()[0]
        pose3d[:,0] = -pose3d[:,0]
        pose3d[:,1] = -pose3d[:,1]

        
        for j in range(pose3d.shape[0]):
            pose3d[j] = global_rot_x.apply(pose3d[j])
            pose3d[j] = global_rot_y.apply(pose3d[j])
        
        rots = get_rot(pose3d)
        
        array = sendToSteamVR("getdevicepose 0")

        if "error" not in array:
            headsetpos = [float(array[3]),float(array[4]),float(array[5])]
            headsetrot = R.from_quat([float(array[7]),float(array[8]),float(array[9]),float(array[6])])
            
            neckoffset = headsetrot.apply(hmd_to_neck_offset)
            
            if recalibrate:
                skelSize = np.max(pose3d, axis=0)-np.min(pose3d, axis=0)-0
                posescale = headsetpos[1]/skelSize[1]
                recalibrate = False
            else:
                pose3d = pose3d * posescale
                print(pose3d)
                offset = pose3d[7] - (headsetpos+neckoffset)
                if not preview_skeleton:
                    for i in [(0,1),(5,2),(6,0)]:
                        joint = pose3d[i[0]] - offset
                        sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} 0 0.8") 
                else:
                    for i in range(17):
                        joint = pose3d[i] - offset
                        sendToSteamVR(f"updatepose {i} {joint[0]} {joint[1]} {joint[2]-2} 1 0 0 0 0 0.8") 

    print("inference time:", time.time()-t0)
    
    if avgconf > 0.3:
        prevpose = pose
    else:
        prevpose = None
        #poses = []
        print("reset...", avgconf)

    #cv2.imshow("out",image)
    #cv2.waitKey(0)
    
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    draw_pose(img,pose,1)
    
    cv2.imshow("out",img)
    if cv2.waitKey(1) == 27:
        print("Exiting... You can close the window after 10 seconds.")
        exit(0)











