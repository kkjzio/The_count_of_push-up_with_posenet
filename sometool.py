
import numpy as py
import math


def cal_ang(point_1, point_2, point_3):
    """
    根据三点坐标计算夹角
    :param point_1: 点1坐标
    :param point_2: 点2坐标
    :param point_3: 点3坐标
    :return: 返回任意角的夹角值，这里只是返回点2的夹角
    """
    a=math.sqrt((point_2[0]-point_3[0])*(point_2[0]-point_3[0])+(point_2[1]-point_3[1])*(point_2[1] - point_3[1]))
    b=math.sqrt((point_1[0]-point_3[0])*(point_1[0]-point_3[0])+(point_1[1]-point_3[1])*(point_1[1] - point_3[1]))
    c=math.sqrt((point_1[0]-point_2[0])*(point_1[0]-point_2[0])+(point_1[1]-point_2[1])*(point_1[1]-point_2[1]))
    # A=math.degrees(math.acos((a*a-b*b-c*c)/(-2*b*c)))
    B=math.degrees(math.acos((b*b-a*a-c*c)/(-2*a*c)))
    # C=math.degrees(math.acos((c*c-a*a-b*b)/(-2*a*b)))
    return B


# d=cal_ang((0, 0), (1, 1), (0, 3))
# print(d)
# 判断三点是否是直线
def ifline_judge(A,B,C,angx=30.0):
    ang=cal_ang(A,B,C)
    if ang>(180.0-angx) :
        return True
    else:
        return False
        
# 判断二点所成直线是否水平
def ifhorize_judge(A,B,angx=45.0):
    # 做出A,B点的对应直角
    C=A[0],B[1]
    ang=cal_ang(A,B,C)
    if ang<angx:
        return True
    else:
        return False

def body_ifline_judge(posedict):
    # 求出两脚踝和膝盖中点
    ankle=(posedict['R_Ankle']+posedict['L_Ankle'])/2.0
    knee=(posedict['R_Knee']+posedict['L_Knee'])/2.0
    # 首先先判断腿、躯干（膝盖、盆骨、胸）是不是直的
    if ifline_judge(ankle,knee,posedict['Pelvis']) and ifline_judge(knee,posedict['Pelvis'],posedict['Thorax']):
        # 再判断是否水平
        if ifhorize_judge(knee,posedict['Thorax']):
            return True

    return False

    
def ankle_ang(posedict):
    # 求出两手腕和肘关节,肩关节中点
    wrist=(posedict['R_Wrist']+posedict['L_Wrist'])/2.0
    elbow=(posedict['R_Elbow']+posedict['L_Elbow'])/2.0
    shoulder=(posedict['R_Shoulder']+posedict['L_Shoulder'])/2.0
    # wrist=posedict['R_Wrist']
    # elbow=posedict['R_Elbow']
    # shoulder=posedict['R_Shoulder']

    ang=cal_ang(wrist,elbow,shoulder)

    return ang
