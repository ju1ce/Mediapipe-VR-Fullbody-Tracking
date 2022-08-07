import tkinter as tk
import sys
import pickle

def set_advanced(window,param):
    param["switch_advanced"] = True
    window.quit()

def getparams():
    
    try:
        param = pickle.load(open("params.p","rb"))
    except:
        param = {}
        
    if "camid" not in param:
        param["camid"] = 'http://192.168.1.103:8080/video'
    if "imgsize" not in param:
        param["imgsize"] = 640
    if "neckoffset" not in param:
        param["neckoffset"] = [0.0, -0.2, 0.1]
    if "prevskel" not in param:
        param["prevskel"] = False
    if "waithmd" not in param:
        param["waithmd"] = False
    if "rotateclock" not in param:
        param["rotateclock"] = False
    if "rotatecclock" not in param: 
        param["rotatecclock"] = False
    if "rotate" not in param:
        param["rotate"] = None
    if "camlatency" not in param:
        param["camlatency"] = 0.05
    if "smooth" not in param:
        param["smooth"] = 0.5
    if "feetrot" not in param:
        param["feetrot"] = False
    if "calib_scale" not in param:
        param["calib_scale"] = True
    if "calib_tilt" not in param:
        param["calib_tilt"] = True
    if "calib_rot" not in param:
        param["calib_rot"] = True
    if "use_hands" not in param:
        param["use_hands"] = False
    if "ignore_hip" not in param:
        param["ignore_hip"] = False
    if "camera_settings" not in param:
        param["camera_settings"] = False
    if "camera_width" not in param:
        param["camera_width"] = 640
    if "camera_height" not in param:
        param["camera_height"] = 480
    if "model_complexity" not in param:
        param["model_complexity"] = 1
    if "smooth_landmarks" not in param:
        param["smooth_landmarks"] = True
    if "min_tracking_confidence" not in param:
        param["min_tracking_confidence"] = 0.5
    if "static_image" not in param:
        param["static_image"] = False    
    if "advanced" not in param:
        param["advanced"] = False
       
    window = tk.Tk()

    def on_close():
        window.destroy()
        sys.exit("INFO: Exiting... You can close the window after 10 seconds.")

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(text="Camera IP or ID:", width = 50).pack()
    camid = tk.Entry(width = 50)
    camid.pack()
    camid.insert(0,param["camid"])
    
    if not param["advanced"]:
        tk.Label(text="NOTE: Increasing resolution may decrease performance.\n Unless you have problems with opening camera, leave it as default.", width = 50).pack()

    tk.Label(text="Camera width:", width = 50).pack()
    camwidth = tk.Entry(width = 20)
    camwidth.pack()
    camwidth.insert(0,param["camera_width"])
    
    tk.Label(text="Camera height:", width = 50).pack()
    camheight = tk.Entry(width = 20)
    camheight.pack()
    camheight.insert(0,param["camera_height"])
    
    if not param["advanced"]:
        tk.Label(text="NOTE: Opening camera settings may change camera behaviour. \nSome cameras may only work with this enabled, some only with this \ndisabled, and it may change which camera ID you have to use.", width = 55).pack()
    
    varcamsettings = tk.IntVar(value = param["camera_settings"])
    cam_settings_check = tk.Checkbutton(text = "Attempt to open camera settings", variable = varcamsettings)
    cam_settings_check.pack()

    if param["advanced"]:
        tk.Label(text="Maximum image size:", width = 50).pack()
        maximgsize = tk.Entry(width = 20)
        maximgsize.pack()
        maximgsize.insert(0,param["imgsize"])

    tk.Label(text="-"*50, width = 50).pack()

    varfeet = tk.IntVar(value = param["feetrot"])
    rot_feet_check = tk.Checkbutton(text = "Enable experimental foot rotation", variable = varfeet)
    rot_feet_check.pack()
    
    if not param["advanced"]:
        tk.Label(text="NOTE: VRChat requires a hip tracker. Only disable it if you \nuse another software for hip tracking, such as owoTrack.", width = 55).pack()
    
    varhip = tk.IntVar(value = param["ignore_hip"])
    hip_check = tk.Checkbutton(text = "Disable hip tracker", variable = varhip)
    hip_check.pack()
    
    tk.Label(text="-"*50, width = 50).pack()
    
    if param["advanced"]:
        
        varhand = tk.IntVar(value = param["use_hands"])
        hand_check = tk.Checkbutton(text = "DEV: Spawn trackers for hands", variable = varhand)
        hand_check.pack()
        
        varskel = tk.IntVar(value = param["prevskel"])
        skeleton_check = tk.Checkbutton(text = "DEV: Preview skeleton in VR", variable = varskel)
        skeleton_check.pack()

        tk.Label(text="-"*50, width = 50).pack()

        tk.Label(text="[ADVANCED] MediaPipe estimator parameters:", width = 50).pack()

        tk.Label(text="Model complexity:", width = 50).pack()
        modelc = tk.Entry(width = 20)
        modelc.pack()
        modelc.insert(0,param["model_complexity"])
        
        varmsmooth = tk.IntVar(value = param["smooth_landmarks"])
        msmooth_check = tk.Checkbutton(text = "Smooth landmarks", variable = varmsmooth)
        msmooth_check.pack()
        
        tk.Label(text="Min tracking confidence:", width = 50).pack()
        trackc = tk.Entry(width = 20)
        trackc.pack()
        trackc.insert(0,param["min_tracking_confidence"])
        
        varstatic = tk.IntVar(value = param["static_image"])
        static_check = tk.Checkbutton(text = "Static image mode", variable = varstatic)
        static_check.pack()
    
    param["switch_advanced"] = False
    if param["advanced"]:
        tk.Label(text="-"*50, width = 50).pack()
        tk.Button(text='Disable advanced mode', command=lambda *args: set_advanced(window,param)).pack()
    else:
        tk.Button(text='Enable advanced mode', command=lambda *args: set_advanced(window,param)).pack()

    tk.Button(text='Save and Continue', command=window.quit).pack()

    window.mainloop()

    cameraid = camid.get()
    #hmd_to_neck_offset = [float(val) for val in hmdoffsettext.get().split(" ")]
    
    dont_wait_hmd = False #bool(varhmdwait.get()) 
    
    #camera_latency = float(camlatencytext.get())
    #smoothing = float(smoothingtext.get())
    feet_rotation = bool(varfeet.get())
    
    ignore_hip = bool(varhip.get())
    camera_settings = bool(varcamsettings.get())
    camera_height = camheight.get()
    camera_width = camwidth.get()
    
    if param["advanced"]:
        maximgsize = int(maximgsize.get())
        
        preview_skeleton = bool(varskel.get())
        use_hands = bool(varhand.get())
        
        mp_smoothing = bool(varmsmooth.get())
        model_complexity = int(modelc.get())
        min_tracking_confidence = float(trackc.get())
        static_image = bool(varstatic.get())
    else:
        maximgsize = 640
        
        preview_skeleton = False
        use_hands = False
        
        mp_smoothing = True
        model_complexity = 1
        min_tracking_confidence = 0.5
        static_image = False

    switch_advanced = param["switch_advanced"]

    advanced = param["advanced"]

    param = {}
    param["camid"] = cameraid
    param["imgsize"] = maximgsize
    #param["neckoffset"] = hmd_to_neck_offset
    param["prevskel"] = preview_skeleton
    param["waithmd"] = dont_wait_hmd

    #param["smooth"] = smoothing
    #param["camlatency"] = camera_latency
    param["feetrot"] = feet_rotation
    param["use_hands"] = use_hands
    param["ignore_hip"] = ignore_hip
    
    param["camera_settings"] = camera_settings
    param["camera_height"] = camera_height
    param["camera_width"] = camera_width
    
    param["model_complexity"] = model_complexity
    param["smooth_landmarks"] = mp_smoothing
    param["static_image"] = static_image
    param["min_tracking_confidence"] = min_tracking_confidence
    
    if switch_advanced:
        param["advanced"] = not advanced
    else:
        param["advanced"] = advanced
    
    pickle.dump(param,open("params.p","wb"))
    
    window.destroy()
    
    if switch_advanced:
        return None
    else:
        return param

if __name__ == "__main__":
    print(getparams())
