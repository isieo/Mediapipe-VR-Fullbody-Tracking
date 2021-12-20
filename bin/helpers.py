import cv2
import numpy as np
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


def mediapipeTo3dpose(lms):
    
    #convert landmarks returned by mediapipe to skeleton that I use.
    #lms = results.pose_world_landmarks.landmark
    
    pose = np.zeros((29,3))

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

    #right foot
    pose[17] = [lms[31].x,lms[31].y,lms[31].z]  #forward
    pose[18] = [lms[29].x,lms[29].y,lms[29].z]  #back  
    pose[19] = [lms[25].x,lms[25].y,lms[25].z]  #up
    
    #left foot
    pose[20] = [lms[32].x,lms[32].y,lms[32].z]  #forward
    pose[21] = [lms[30].x,lms[30].y,lms[30].z]  #back
    pose[22] = [lms[26].x,lms[26].y,lms[26].z]  #up
    
    #right hand
    pose[23] = [lms[17].x,lms[17].y,lms[17].z]  #forward
    pose[24] = [lms[15].x,lms[15].y,lms[15].z]  #back
    pose[25] = [lms[19].x,lms[19].y,lms[19].z]  #up
    
    #left hand
    pose[26] = [lms[18].x,lms[18].y,lms[18].z]  #forward
    pose[27] = [lms[16].x,lms[16].y,lms[16].z]  #back
    pose[28] = [lms[20].x,lms[20].y,lms[20].z]  #up

    return pose

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

def get_rot_hands(pose3d):

    hand_r_f = pose3d[26]
    hand_r_b = pose3d[27]
    hand_r_u = pose3d[28]
    
    hand_l_f = pose3d[23]
    hand_l_b = pose3d[24]
    hand_l_u = pose3d[25]
    
    # left hand
    
    x = hand_l_f - hand_l_b
    w = hand_l_u - hand_l_b
    z = np.cross(x, w)
    y = np.cross(z, x)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    l_hand_rot = np.vstack((z, y, -x)).T
    
    # right hand
    
    x = hand_r_f - hand_r_b
    w = hand_r_u - hand_r_b
    z = np.cross(x, w)
    y = np.cross(z, x)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    r_hand_rot = np.vstack((z, y, -x)).T

    r_hand_rot = R.from_matrix(r_hand_rot).as_quat()
    l_hand_rot = R.from_matrix(l_hand_rot).as_quat()
    
    return l_hand_rot, r_hand_rot

def get_rot_mediapipe(pose3d):
    hip_left = pose3d[2]
    hip_right = pose3d[3]
    hip_up = pose3d[16]
      
    foot_r_f = pose3d[17]
    foot_r_b = pose3d[18]
    foot_r_u = pose3d[19]

    foot_l_f = pose3d[20]
    foot_l_b = pose3d[21]
    foot_l_u = pose3d[22]
    
    # hip
    
    x = hip_right - hip_left
    w = hip_up - hip_left
    z = np.cross(x, w)
    y = np.cross(z, x)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    hip_rot = np.vstack((x, y, z)).T
    
    # left foot
    
    x = foot_l_f - foot_l_b
    w = foot_l_u - foot_l_b
    z = np.cross(x, w)
    y = np.cross(z, x)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    l_foot_rot = np.vstack((x, y, z)).T
    
    # right foot
    
    x = foot_r_f - foot_r_b
    w = foot_r_u - foot_r_b
    z = np.cross(x, w)
    y = np.cross(z, x)
    
    x = x/np.sqrt(sum(x**2))
    y = y/np.sqrt(sum(y**2))
    z = z/np.sqrt(sum(z**2))
    
    r_foot_rot = np.vstack((x, y, z)).T
    
    hip_rot = R.from_matrix(hip_rot).as_quat()
    r_foot_rot = R.from_matrix(r_foot_rot).as_quat()
    l_foot_rot = R.from_matrix(l_foot_rot).as_quat()
    
    return hip_rot, l_foot_rot, r_foot_rot

    

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
