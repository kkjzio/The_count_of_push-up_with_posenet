from PIL import Image
import cv2
import numpy as np
import os.path as osp
import sys

from torch.nn.modules.module import T
from yolo import YOLO
from ROOTNET.demo import demo
from POSENET.demo import demo1
from sometool import body_ifline_judge,ankle_ang

yolo = YOLO()
cam = cv2.VideoCapture('video.mp4')
# cam = cv2.VideoCapture(0)
# width = 640  # 定义摄像头获取图像宽度
# height = 368   # 定义摄像头获取图像长度

# cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)  #设置宽度
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  #设置长度
joints_name = ('Head_top', 'Thorax', 'R_Shoulder', 'R_Elbow', 'R_Wrist', 'L_Shoulder', 'L_Elbow', 'L_Wrist', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee', 'L_Ankle', 'Pelvis', 'Spine', 'Head', 'R_Hand', 'L_Hand', 'R_Toe', 'L_Toe')
num = 0
sz = (int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
      int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fps = 24
# 默认手臂伸直时为1
flag=1
tt=flag
count=0
ang=0.0

fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
vout_1 = cv2.VideoWriter()
vout_1.open('./out_vedio.mp4', fourcc, fps, sz, True)
while (cam.isOpened()):
    ret, frame = cam.read()
    if ret==True:
        # frame = cv2.resize(frame,(372, 495), interpolation=cv2.INTER_CUBIC)
        # try:
        # 转换为PIL格式
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # Yolov3给出标记的图片r_image和box信息bbox_list
        r_image, bbox_list = yolo.detect_image(image)
        # print(bbox_list)
        # 转回为cv2格式
        img = cv2.cvtColor(np.asarray(r_image), cv2.COLOR_RGB2BGR)
        for i in range(len(bbox_list)):
            x, y = bbox_list[i][1], bbox_list[i][0]
            bbox_list[i][1], bbox_list[i][0] = y, x
            x, y = bbox_list[i][2], bbox_list[i][3]
            bbox_list[i][2], bbox_list[i][3] = y-bbox_list[i][0], x-bbox_list[i][1]
        try:
            #这里将box信息放入rootnet（root和pose）中提取出人体各位置坐标
            root_list = demo.rootnet(frame, bbox_list)
            # 输出pose_img为处理后的图片，vis_kps为人体各部位坐标，shape为(3,21),代表xyz轴和21个部位
            # z坐标没有用上，全部默认为1
            pose_img, vis_kps = demo1.posenet(img, bbox_list, root_list, num)
            # print(vis_kps)
            # 将对应关节部位换为字典
            posedict={}
            bodyl= False
            for i,str in enumerate(joints_name):
                posedict[str]=np.array((vis_kps[0][i],vis_kps[1][i]))

            # 判断是否在push-up
            bodyl = body_ifline_judge(posedict)
            if bodyl:
                ang=ankle_ang(posedict)
                #给予中间缓冲区间
                if ang > 150.0:
                    flag=1
                elif ang < 110.0:
                    flag=0
                # 当手臂状态改变时，且手臂为弯曲状态时计数
                if tt != flag:
                    tt=flag
                    if flag==0:
                        count+=1

            print(ang)
            pose_img = cv2.putText(pose_img, "push-up= %.2f,count=%.2f,ea=%.2f"%(bodyl,count,ang), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # pose_img = cv2.cvtColor(np.asarray(pose_img), cv2.COLOR_RGB2BGR)
            # pose_img = cv2.cvtColor(pose_img, cv2.COLOR_BGR2RGB)
        except:
            #当yolo bbox_list输出[[0 0 0 0]]时认为此时无输出
            print(bbox_list)    
        vout_1.write(pose_img)
        num += 1

        if cv2.waitKey(1) & 0xFF == ord("w"):
            vout_1.release()
            cam.release()
            break

    else:
        break

print('count=%.2f'%(count))
cam.release()
vout_1.release()
