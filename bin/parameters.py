from guitest import getparams
from scipy.spatial.transform import Rotation as R
import cv2
import tkinter as tk

class Parameters():
    def __init__(self) -> None:
        param = getparams()

        #PARAMETERS:
        #model =  1          #TODO: add parameter for which model size to use
        self.maximgsize = param["imgsize"]               #to prevent working with huge images, images that have one axis larger than this value will be downscaled.
        self.cameraid = param["camid"]                    #to use with an usb or virtual webcam. If 0 doesnt work/opens wrong camera, try numbers 1-5 or so
        #cameraid = "http://192.168.1.102:8080/video"   #to use ip webcam, uncomment this line and change to your ip
        self.hmd_to_neck_offset = param["neckoffset"]    #offset of your hmd to the base of your neck, to ensure the tracking is stable even if you look around. Default is 20cm down, 10cm back.
        self.preview_skeleton = param["prevskel"]             #if True, whole skeleton will appear in vr 2 meters in front of you. Good to visualize if everything is working
        self.dont_wait_hmd = param["waithmd"]                  #dont wait for movement from hmd, start inference immediately.
        self.rotate_image = param["rotate"] # cv2.ROTATE_90_CLOCKWISE # cv2.ROTATE_90_COUTERCLOCKWISE # cv2.ROTATE_180 # None # if you want, rotate the camera
        self.camera_latency = param["camlatency"]
        self.smoothing = param["smooth"]
        self.feet_rotation = param["feetrot"]
        self.calib_scale = param["calib_scale"]
        self.calib_tilt = param["calib_tilt"]
        self.calib_rot = param["calib_rot"]
        self.use_hands = param["use_hands"]
        self.ignore_hip = param["ignore_hip"]

        self.prev_smoothing = self.smoothing

        self.recalibrate = False

        self.global_rot_y = R.from_euler('y',0,degrees=True)     #default rotations, for 0 degrees around y and x
        self.global_rot_x = R.from_euler('x',0,degrees=True) 
        self.global_rot_z = R.from_euler('z',0,degrees=True) 

        self.posescale = 1     

        self.exit_ready = False

        self.img_rot_dict = {0: None, 1: cv2.ROTATE_90_CLOCKWISE, 2: cv2.ROTATE_180, 3: cv2.ROTATE_90_COUNTERCLOCKWISE}

        # trace variables
        
        #self.root = tk.Tk()
        #self.rot_y_var = tk.DoubleVar(value=self.global_rot_y.as_euler('zyx', degrees=True)[1])


    
    def change_recalibrate(self):
        self.recalibrate = True


    def rot_change_y(self, value):                                  #callback functions. Whenever the value on sliders are changed, they are called
        print(f"Changed y rotation value to {value}")
        self.global_rot_y = R.from_euler('y',value,degrees=True)     #and the rotation is updated with the new value.
        

    def rot_change_x(self, value):
        print(f"Changed x rotation value to {value}")
        self.global_rot_x = R.from_euler('x',value-90,degrees=True) 
        
    def rot_change_z(self, value):
        print(f"Changed z rotation value to {value}")
        self.global_rot_z = R.from_euler('z',value-180,degrees=True) 
         

    def change_scale(self, value):
        print(f"Changed scale value to {value}")
        #posescale = value/50 + 0.5
        self.posescale = value


    def change_img_rot(self, val):
        print(f"Changed image rotation to {val*90} clockwise")
        self.rotate_image = self.img_rot_dict[val]


    def change_smoothing(self, val):
        print(f"Changed smoothing value to {val}")
        self.smoothing = val


    def ready2exit(self):
        self.exit_ready = True


if __name__ == "__main__":
    print("hehe")