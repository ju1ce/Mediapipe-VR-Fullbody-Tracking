from init_gui import getparams
from scipy.spatial.transform import Rotation as R
import cv2
import json

class Parameters():
    def __init__(self) -> None:
        param = getparams()
        
        self.model = param["model_complexity"]
        self.smooth_landmarks = param["smooth_landmarks"]
        self.min_tracking_confidence = param["min_tracking_confidence"]

        #PARAMETERS:
        #model =  1          #TODO: add parameter for which model size to use
        self.maximgsize = param["imgsize"]               #to prevent working with huge images, images that have one axis larger than this value will be downscaled.
        self.cameraid = param["camid"]                    #to use with an usb or virtual webcam. If 0 doesnt work/opens wrong camera, try numbers 1-5 or so
        #cameraid = "http://192.168.1.102:8080/video"   #to use ip webcam, uncomment this line and change to your ip
        self.hmd_to_neck_offset = [0,-0.2,0.1]    #offset of your hmd to the base of your neck, to ensure the tracking is stable even if you look around. Default is 20cm down, 10cm back.
        self.preview_skeleton = param["prevskel"]             #if True, whole skeleton will appear in vr 2 meters in front of you. Good to visualize if everything is working
        self.dont_wait_hmd = param["waithmd"]                  #dont wait for movement from hmd, start inference immediately.
        self.rotate_image = 0 # cv2.ROTATE_90_CLOCKWISE # cv2.ROTATE_90_COUTERCLOCKWISE # cv2.ROTATE_180 # None # if you want, rotate the camera
        #self.camera_latency = param["camlatency"]
        #self.smoothing = param["smooth"]
        self.camera_latency = 0.1
        self.smoothing_1 = 0.5
        self.additional_smoothing_1 = 0
        self.smoothing_2 = 0.5
        self.additional_smoothing_2 = 0
        self.feet_rotation = param["feetrot"]
        self.use_hands = param["use_hands"]
        self.ignore_hip = param["ignore_hip"]
        
        self.camera_settings = param["camera_settings"]
        self.camera_width = param["camera_width"]
        self.camera_height = param["camera_height"]

        self.calib_rot = True
        self.calib_tilt = True
        self.calib_scale = True

        self.recalibrate = False

        self.global_rot_y = R.from_euler('y',0,degrees=True)     #default rotations, for 0 degrees around y and x
        self.global_rot_x = R.from_euler('x',0,degrees=True) 
        self.global_rot_z = R.from_euler('z',0,degrees=True) 

        self.posescale = 1     

        self.exit_ready = False

        self.img_rot_dict = {0: None, 1: cv2.ROTATE_90_CLOCKWISE, 2: cv2.ROTATE_180, 3: cv2.ROTATE_90_COUNTERCLOCKWISE}
        self.img_rot_dict_rev = {None: 0, cv2.ROTATE_90_CLOCKWISE: 1, cv2.ROTATE_180: 2, cv2.ROTATE_90_COUNTERCLOCKWISE: 3}

        self.paused = False
        
        self.flip = False
        
        self.log_frametime = False

        self.load_params()
        
        self.smoothing = self.smoothing_1
        self.additional_smoothing = self.additional_smoothing_1
        
        #self.prev_smoothing = self.smoothing
    
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


    def change_smoothing(self, val, paramid = 0):
        print(f"Changed smoothing value to {val}")
        self.smoothing = val
        
        if paramid == 1:
            self.smoothing_1 = val
        if paramid == 2:
            self.smoothing_2 = val
        
    def change_additional_smoothing(self, val, paramid = 0):
        print(f"Changed additional smoothing value to {val}")
        self.additional_smoothing = val

        if paramid == 1:
            self.additional_smoothing_1 = val
        if paramid == 2:
            self.additional_smoothing_2 = val

    def change_camera_latency(self, val):
        print(f"Changed camera latency to {val}")
        self.camera_latency = val

    def change_neck_offset(self,x,y,z):
        print(f"Hmd to neck offset changed to: [{x},{y},{z}]")
        self.hmd_to_neck_offset = [x,y,z]

    def ready2exit(self):
        self.exit_ready = True


    def save_params(self):
        param = {}
        param["rotate"] = self.img_rot_dict_rev[self.rotate_image] 
        param["smooth1"] = self.smoothing_1
        param["smooth2"] = self.smoothing_2

        param["camlatency"] = self.camera_latency
        param["addsmooth1"] = self.additional_smoothing_1
        param["addsmooth2"] = self.additional_smoothing_2

        #if self.flip:
        param["roty"] = 180-self.global_rot_y.as_euler('zyx', degrees=True)[1]
        param["rotx"] = self.global_rot_x.as_euler('zyx', degrees=True)[2]
        param["rotz"] = self.global_rot_z.as_euler('zyx', degrees=True)[0] 
        param["scale"] = self.posescale
        
        param["calibrot"] = self.calib_rot
        param["calibtilt"] = self.calib_tilt
        param["calibscale"] = self.calib_scale
        
        param["flip"] = self.flip
        
        param["hmd_to_neck_offset"] = self.hmd_to_neck_offset
        
        print(param["roty"])
        
        with open("saved_params.json", "w") as f:
            json.dump(param, f)

    def load_params(self):

        try:
            with open("saved_params.json", "r") as f:
                param = json.load(f)

            print(param["roty"])

            self.rotate_image = self.img_rot_dict[param["rotate"]]
            self.smoothing_1 = param["smooth1"]
            self.smoothing_2 = param["smooth2"]
            self.camera_latency = param["camlatency"]
            self.additional_smoothing_1 = param["addsmooth1"]
            self.additional_smoothing_2 = param["addsmooth2"]

            self.global_rot_y = R.from_euler('y',param["roty"],degrees=True)
            self.global_rot_x = R.from_euler('x',param["rotx"],degrees=True)
            self.global_rot_z = R.from_euler('z',param["rotz"],degrees=True)
            self.posescale = param["scale"]
            
            self.calib_rot = param["calibrot"]
            self.calib_tilt = param["calibtilt"]
            self.calib_scale = param["calibscale"]
            
            self.hmd_to_neck_offset = param["hmd_to_neck_offset"]
            
            self.flip = param["flip"]
        except:
            print("Save file not found, will be created after you exit the program.")
 


if __name__ == "__main__":
    print("hehe")