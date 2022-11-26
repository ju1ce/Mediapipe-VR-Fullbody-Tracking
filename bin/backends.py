import time
from abc import ABC, abstractmethod
from helpers import  sendToSteamVR
from scipy.spatial.transform import Rotation as R

class Backend(ABC):

    @abstractmethod
    def onparamchanged(self, params):
        ...

    @abstractmethod
    def connect(self, params):
        ...

    @abstractmethod
    def updatepose(self, params, pose3d, rots, hand_rots):
        ...

    @abstractmethod
    def disconnect(self):
        ...

class DummyBackend(Backend):

    def __init__(self, **kwargs):
        pass

    def onparamchanged(self, params):
        pass

    def connect(self, params):
        pass

    def updatepose(self, params, pose3d, rots, hand_rots):
        pass

    def disconnect(self):
        pass

class SteamVRBackend(Backend):

    def __init__(self, **kwargs):
        pass

    def onparamchanged(self, params):
        resp = sendToSteamVR(f"settings 50 {self.smoothing} {self.additional_smoothing}")
        while "error" in resp:
            resp = sendToSteamVR(f"settings 50 {self.smoothing} {self.additional_smoothing}")
            print(resp)
            time.sleep(1)

    def connect(self, params):
        print("Connecting to SteamVR")

        #ask the driver, how many devices are connected to ensure we dont add additional trackers
        #in case we restart the program
        numtrackers = sendToSteamVR("numtrackers")
        for i in range(10):
            if "error" in numtrackers:
                print("Error while connecting to SteamVR. Retrying...")
                time.sleep(1)
                numtrackers = sendToSteamVR("numtrackers")
            else:
                break

        if "error" in numtrackers:
            print("Could not connect to SteamVR after 10 tries!")
            time.sleep(10)
            assert 0, "Could not connect to SteamVR after 10 tries"

        numtrackers = int(numtrackers[2])

        #games use 3 trackers, but we can also send the entire skeleton if we want to look at how it works
        totaltrackers = 23 if params.preview_skeleton else  3
        if params.use_hands:
            totaltrackers = 5
        if params.ignore_hip:
            totaltrackers -= 1

        roles = ["TrackerRole_Waist", "TrackerRole_RightFoot", "TrackerRole_LeftFoot"]

        if params.ignore_hip and not params.preview_skeleton:
            del roles[0]

        if params.use_hands:
            roles.append("TrackerRole_Handed")
            roles.append("TrackerRole_Handed")

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

        resp = sendToSteamVR(f"settings 50 {params.smoothing} {params.additional_smoothing}")
        while "error" in resp:
            resp = sendToSteamVR(f"settings 50 {params.smoothing} {params.additional_smoothing}")
            print(resp)
            time.sleep(1)

    def updatepose(self, params, pose3d, rots, hand_rots):
        array = sendToSteamVR("getdevicepose 0")        #get hmd data to allign our skeleton to

        if "error" in array:    #continue to next iteration if there is an error
            return False

        headsetpos = [float(array[3]),float(array[4]),float(array[5])]
        headsetrot = R.from_quat([float(array[7]),float(array[8]),float(array[9]),float(array[6])])

        neckoffset = headsetrot.apply(params.hmd_to_neck_offset)   #the neck position seems to be the best point to allign to, as its well defined on
                                                            #the skeleton (unlike the eyes/nose, which jump around) and can be calculated from hmd.

        if params.recalibrate:
            print("frame to recalibrate")

        else:
            pose3d = pose3d * params.posescale     #rescale skeleton to calibrated height
            #print(pose3d)
            offset = pose3d[7] - (headsetpos+neckoffset)    #calculate the position of the skeleton
            if not params.preview_skeleton:
                numadded = 3
                if not params.ignore_hip:
                    for i in [(0,1),(5,2),(6,0)]:
                        joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                        sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} {params.camera_latency} 0.8")
                else:
                    for i in [(0,1),(5,2)]:
                        joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                        sendToSteamVR(f"updatepose {i[1]} {joint[0]} {joint[1]} {joint[2]} {rots[i[1]][3]} {rots[i[1]][0]} {rots[i[1]][1]} {rots[i[1]][2]} {params.camera_latency} 0.8")
                        numadded = 2
                if params.use_hands:
                    for i in [(10,0),(15,1)]:
                        joint = pose3d[i[0]] - offset       #for each foot and hips, offset it by skeleton position and send to steamvr
                        sendToSteamVR(f"updatepose {i[1]+numadded} {joint[0]} {joint[1]} {joint[2]} {hand_rots[i[1]][3]} {hand_rots[i[1]][0]} {hand_rots[i[1]][1]} {hand_rots[i[1]][2]} {params.camera_latency} 0.8")
            else:
                for i in range(23):
                    joint = pose3d[i] - offset      #if previewing skeleton, send the position of each keypoint to steamvr without rotation
                    sendToSteamVR(f"updatepose {i} {joint[0]} {joint[1]} {joint[2] - 2} 1 0 0 0 {params.camera_latency} 0.8")
        return True

    def disconnect(self):
        pass
