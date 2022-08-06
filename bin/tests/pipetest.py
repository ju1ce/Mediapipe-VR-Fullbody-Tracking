import time
import sys
from scipy.spatial.transform import Rotation as R

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
    

def main():
    #this file is just for pipe testing purposes
    sendToSteamVR("settings 5 2")
    assert 0

    pipe = open(r'\\.\pipe\ApriltagPipeIn', 'rb+', buffering=0)

    some_data = str.encode("numtrackers")
    pipe.write(some_data)
    resp = pipe.read(1024)
    string = resp.decode("utf-8")
    print(string)

    array = string.split(" ")

    print(array)
    print(int(array[2]))

    numtrackers = int(array[2])

    for i in range(numtrackers,1):

        pipe.close()
        pipe = open(r'\\.\pipe\ApriltagPipeIn', 'rb+', buffering=0)

        some_data = str.encode("addtracker")
        pipe.write(some_data)
        resp = pipe.read(1024)
        string = resp.decode("utf-8")
        print(string)

        pipe.close()

    pipe = open(r'\\.\pipe\ApriltagPipeIn', 'rb+', buffering=0)

    some_data = str.encode("getdevicepose 0")
    pipe.write(some_data)
    resp = pipe.read(1024)
    string = resp.decode("utf-8")
    print(string)

    while True:
        array = sendToSteamVR("getdevicepose 0")
        
        if "error" in array:
            continue
            
        hmdrot = [float(array[7]),float(array[8]),float(array[9]),float(array[6])]
        hmdpos = [float(array[3]),float(array[4]),float(array[5])]
        
        r = R.from_quat(hmdrot)
        
        pos = r.apply([0,-0.2,-0.15]) + hmdpos
        
        sendToSteamVR(f"updatepose {0} {pos[0]} {pos[1]} {pos[2]} 1 0 0 0 0 0.8")
        
        print(pos)


if __name__ == "__main__":
    main()
    
    
    