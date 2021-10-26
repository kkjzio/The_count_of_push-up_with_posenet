结果展示在目录下

主体文件为目录下的predict.py文件

**使用前请先将3个pth权重文件解压至model_data目录下**

环境配置具体在目录下的requirement.txt中，常用包不在其中

~~程序在Linux下运行测试成功，尚且不确定win下的情况，如果报错，有可能是文件路径的问题，请将~~

~~ROOTNET/demo/demo.py~~

~~POSENET/demo/demo1.py~~

~~yolo.py~~

~~中有路径的字符串中的"/"改成“\”~~

------

权重pth下载地址：

链接：https://pan.baidu.com/s/10Hn_N_2VaQrmyYQajbKcyg 
提取码：r4tx 




## 问题1 判断视频中的人物俯卧撑的个数并实时显示



```python
# 视频输入位置
cam = cv2.VideoCapture('video.mp4')
...
# 视频输出位置
vout_1.open('./out_vedio.mp4', fourcc, fps, sz, True)
```



大体思路主要分为四部分：

1. 利用yoloV3提取出方框，减少图片大小加快后续步骤速度
2. 利用方框位置输入给rootnet提取出人体姿态
3. 利用人体姿态信息判断俯卧撑
4. 利用手肘夹角判定做的次数



### yolo

主要文件为目录下的yolo.py，关键位置在文件yolo.py中的119、178行，比起原来的文件增加了位置框的输出.在predict.py中的对应代码在43行。

### rootnet

主要文件为ROOTNET/demo/demo和POSENET/demo/demo1两个，在predicr.py中对应54、57主要功能是通过输入的图片和bbox位置提取出人体各个部位的坐标信息。

### push-up姿态判断

这里我也大概分为了两个阶段去判断：

1. 人的腿、躯干是否笔直

   这里对应sometool.py文件中的26 、34中的ifline_judge

   大体思路是用身体的三个点计算出中间点的角度，只要角度符合预设值就判断为笔直

2. 人的全体是否和水平面平行

   这里对应sometool.py文件中的34中ifhorize_judge函数

   依据两个点做出其对应的水平直角，这个水平的直接边是平行的，然后再计算两点所成的边与这个平行边的夹角，进而判断两点所成的边是否平行于水平面

判断1后再判断2进而判断姿态是否水平，依据这个判定是否正在做俯卧撑。

### 俯卧撑计数

首先得先满足上面姿势判断的条件才会到这（对应predict.py的67行）

我用的判断方式是手肘的夹角（对应sometool.py中的56行以及predict.py中的70-78行），大体思路是超过某个角度或者小于某个角度后，就对手柄是弯曲还是笔直做判定，如果手臂状态由笔直变为弯曲，那么计数+1。



### 问题2 修改已有网络中的权重

我的理解是将网络中的权重加载出来另存和加载，并且能够对其中的权重进行修改，具体注释和实现方法在saveweight.py中

------

参考：

https://github.com/faheinrich/moon_pose_estimation_setup

https://github.com/mks0601/3DMPPE_POSENET_RELEASE

