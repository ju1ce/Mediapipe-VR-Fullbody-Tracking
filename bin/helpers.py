import cv2
import numpy as np
import tensorflow as tf
from scipy.spatial.transform import Rotation as R

# Dictionary that maps from joint names to keypoint indices.
KEYPOINT_DICT = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
}

EDGES = [
    (0, 1),
    (0, 2),
    (1, 3),
    (2, 4),
    (0, 5),
    (0, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 6),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16)
]

skeleton3d = ((0,1),(1,2),(5,4),(4,3),(2,6),(3,6),(6,16),(16,7),(7,8),(8,9),(7,12),(7,13),(10,11),(11,12),(15,14),(14,13)) #head is 9, one hand is 10, other is 15


def draw_pose(frame,pose,size):
    pose = pose*size
    for sk in EDGES:
        cv2.line(frame,(int(pose[sk[0],1]),int(pose[sk[0],0])),(int(pose[sk[1],1]),int(pose[sk[1],0])),(0,255,0),3)

def get_bbox(img,points,imgsize):
    
    #print(points.shape)
    #points = np.reshape(points,(-1,2), order="C")
    
    startsize = max(img.shape)
    #print(startsize)
    
    kleft = min(points[:,0])
    kright = max(points[:,0])
    kbottom = min(points[:,1])
    ktop = max(points[:,1])
    kcenter = ((kright+kleft)/2,(ktop+kbottom)/2)
    ksize = max([kright-kleft,ktop-kbottom]) * 1.3
    kleftcorner = (kcenter[0]-ksize/2,kcenter[1]-ksize/2)
    
    #print(kcenter)
    #print(ksize)
    #print(img.shape)
    
    scenter = [kcenter[0]/img.shape[1],kcenter[1]/img.shape[2]]
    ssize = [ksize/(2*img.shape[1]),ksize/(2*img.shape[2])]
    
    bboxes = [[scenter[0]-ssize[0],scenter[1]-ssize[1],scenter[0]+ssize[0],scenter[1]+ssize[1]]]

    #print(bboxes)
    
    img = tf.image.crop_and_resize(img,bboxes,[0],[imgsize,imgsize])

    return img, kcenter, ksize

def keypoints_to_original(scale,center,points):
    scores = points[:,2]
    points -= 0.5
    #print(scale,center)
    #print(points)
    points *= scale
    #print(points)
    points[:,0] += center[0]
    points[:,1] += center[1]
    #print(points)
    
    points[:,2] = scores
    
    return points

def normalize_screen_coordinates(X, w, h):
    assert X.shape[-1] == 2

    # Normalize so that [0, w] is mapped to [-1, 1], while preserving the aspect ratio
    return X / w * 2 - [1, h / w]

def get_rot(pose3d):

    ## guesses
    hip_left = 2
    hip_right = 3
    hip_up = 16
    
    knee_left = 1
    knee_right = 4
    
    ankle_left = 0
    ankle_right = 5
    
    # hip
    
    x = pose3d[hip_right] - pose3d[hip_left]
    w = pose3d[hip_up] - pose3d[hip_left]
    z = np.cross(x, w)
    y = np.cross(z, x)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    hip_rot = np.vstack((x, y, z)).T

    # right leg
    
    y = pose3d[knee_right] - pose3d[ankle_right]
    w = pose3d[hip_right] - pose3d[ankle_right]
    z = np.cross(w, y)
    if np.sqrt(sum(z**2)) < 1e-6:
        w = pose3d[hip_left] - pose3d[ankle_left]
        z = np.cross(w, y)
    x = np.cross(y,z)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    leg_r_rot = np.vstack((x, y, z)).T

    # left leg
    
    y = pose3d[knee_left] - pose3d[ankle_left]
    w = pose3d[hip_left] - pose3d[ankle_left]
    z = np.cross(w, y)
    if np.sqrt(sum(z**2)) < 1e-6:
        w = pose3d[hip_right] - pose3d[ankle_left]
        z = np.cross(w, y)
    x = np.cross(y,z)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    leg_l_rot = np.vstack((x, y, z)).T

    rot_hip = R.from_matrix(hip_rot).as_quat()
    rot_leg_r = R.from_matrix(leg_r_rot).as_quat()
    rot_leg_l = R.from_matrix(leg_l_rot).as_quat()
    
    return rot_hip, rot_leg_l, rot_leg_r