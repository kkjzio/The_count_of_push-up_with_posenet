from yolo import YOLO
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# 将找到的卷积和全连接层参数置0
def zero_param(self):
    for m in self.modules():
        if isinstance(m, nn.Conv2d):
            torch.nn.init.constant_(m.weight.data, 0)
            if m.bias is not None:
                m.bias.data.zero_()
        elif isinstance(m, nn.Linear):
            torch.nn.init.constant_(m.weight.data, 0)
            m.bias.data.zero_()


yolo=YOLO()

# 获取网络当前参数
net_state_dict = yolo.net.state_dict()

print('net_state_dict类型：', type(net_state_dict))
print('net_state_dict管理的参数: ', net_state_dict.keys())
for key, value in net_state_dict.items():
    print('参数名: ', key, '\t大小: ',  value.shape)

# 保存，并加载模型参数(仅保存模型参数)
torch.save(yolo.net.state_dict(), 'net_params.pkl')   # 假设训练好了一个模型net
pretrained_dict = torch.load('net_params.pkl')

# 将net的参数全部置0，方便对比
zero_param(yolo.net)
net_state_dict = yolo.net.state_dict()
print('conv1层的权值为:\n', net_state_dict['module.backbone.conv1.weight'], '\n')

# 通过load_state_dict 加载参数
yolo.net.load_state_dict(pretrained_dict)
print('加载之后，conv1层的权值变为:\n', net_state_dict['module.backbone.conv1.weight'])
