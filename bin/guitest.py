import tkinter as tk
import pickle
import cv2

def getparams():
    
    try:
        param = pickle.load(open("params.p","rb"))
    except:
        param = {}
        param["camid"] = 'http://192.168.1.103:8080/video'
        param["imgsize"] = 800
        param["neckoffset"] = [0.0, -0.2, 0.1]
        param["prevskel"] = False
        param["waithmd"] = False
        param["rotateclock"] = False
        param["rotatecclock"] = False
        param["rotate"] = None

    window = tk.Tk()

    tk.Label(text="Camera IP or ID:", width = 50).pack()
    camid = tk.Entry(width = 50)
    camid.pack()
    camid.insert(0,param["camid"])

    tk.Label(text="Maximum image size:", width = 50).pack()
    maximgsize = tk.Entry(width = 20)
    maximgsize.pack()
    maximgsize.insert(0,param["imgsize"])

    tk.Label(text="Offset of HMD to neck:", width = 50).pack()
    hmdoffsettext = tk.Entry(width = 50)
    hmdoffsettext.pack()
    hmdoffsettext.insert(0," ".join(map(str,param["neckoffset"])))

    varskel = tk.IntVar(value = param["prevskel"])
    skeleton_check = tk.Checkbutton(text = "Preview whole skeleton", variable = varskel)
    skeleton_check.pack()

    varhmdwait = tk.IntVar(value = param["waithmd"])
    hmdwait_check = tk.Checkbutton(text = "Dont wait for hmd", variable = varhmdwait)
    hmdwait_check.pack()

    varclock = tk.IntVar(value = param["rotateclock"])
    rot_clock_check = tk.Checkbutton(text = "Rotate camera clockwise", variable = varclock)
    rot_clock_check.pack()

    varcclock = tk.IntVar(value = param["rotatecclock"])
    rot_cclock_check = tk.Checkbutton(text = "Rotate camera counter clockwise", variable = varcclock)
    rot_cclock_check.pack()

    tk.Button(text='Save and continue', command=window.quit).pack()

    window.mainloop()

    cameraid = camid.get()
    maximgsize = int(maximgsize.get())
    hmd_to_neck_offset = [float(val) for val in hmdoffsettext.get().split(" ")]
    preview_skeleton = bool(varskel.get())
    dont_wait_hmd = bool(varhmdwait.get())
    if varclock.get():
        if varcclock.get():
            rotate_image = cv2.ROTATE_180
        else:
            rotate_image = cv2.ROTATE_90_CLOCKWISE
    elif varcclock.get():
        rotate_image = cv2.ROTATE_90_COUNTERCLOCKWISE
    else:
        rotate_image = None

    param = {}
    param["camid"] = cameraid
    param["imgsize"] = maximgsize
    param["neckoffset"] = hmd_to_neck_offset
    param["prevskel"] = preview_skeleton
    param["waithmd"] = dont_wait_hmd
    param["rotateclock"] = bool(varclock.get())
    param["rotatecclock"] = bool(varcclock.get())
    param["rotate"] = rotate_image

    pickle.dump(param,open("params.p","wb"))
    
    window.destroy()
    
    return param

if __name__ == "__main__":
    print(getparams());
