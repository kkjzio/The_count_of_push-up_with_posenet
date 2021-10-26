import sys
import os
import os.path as osp
import argparse
import numpy as np
import cv2
import math
import torch
import torchvision.transforms as transforms
from torch.nn.parallel.data_parallel import DataParallel
import torch.backends.cudnn as cudnn

sys.path.insert(0, osp.join(r'ROOTNET/', 'main'))
sys.path.insert(0, osp.join(r'ROOTNET/', 'data'))
sys.path.insert(0, osp.join(r'ROOTNET/', 'common'))
sys.path.insert(0, osp.join(r'ROOTNET/common/', 'nets'))
sys.path.insert(0, osp.join(r'ROOTNET/common/', 'utils1'))
from config import cfg
from model import get_pose_net
from pose_utils import process_bbox
from dataset import generate_patch_image

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=str, default='0', dest='gpu_ids')
    parser.add_argument('--test_epoch', type=str, default='18', dest='test_epoch')
    args = parser.parse_args()

    # test gpus
    if not args.gpu_ids:
        assert 0, "Please set proper gpu ids"

    if '-' in args.gpu_ids:
        gpus = args.gpu_ids.split('-')
        gpus[0] = 0 if not gpus[0].isdigit() else int(gpus[0])
        gpus[1] = len(mem_info()) if not gpus[1].isdigit() else int(gpus[1]) + 1
        args.gpu_ids = ','.join(map(lambda x: str(x), list(range(*gpus))))

    assert args.test_epoch, 'Test epoch is required.'
    return args

# argument parsing
args = parse_args()
cfg.set_args(args.gpu_ids)
cudnn.benchmark = True

# snapshot load
# model_path = r'Your model storage path' % int(args.test_epoch)
model_path = r'model_data/snapshot_18.pth'
assert osp.exists(model_path), 'Cannot find model at ' + model_path
print('Load checkpoint from {}'.format(model_path))
model = get_pose_net(cfg, False)
model = DataParallel(model).cuda()
ckpt = torch.load(model_path)
model.load_state_dict(ckpt['network'])
model.eval()


def rootnet(img, bboxlist):
# prepare input image
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=cfg.pixel_mean, std=cfg.pixel_std)])
    original_img = img
    original_img_height, original_img_width = original_img.shape[:2]

    bbox_list = bboxlist
    person_num = len(bbox_list)
    root_list = []
    # normalized camera intrinsics
    focal = [1500, 1500]  # x-axis, y-axis
    for n in range(person_num):
        bbox = process_bbox(np.array(bbox_list[n]), original_img_width, original_img_height)
        img, img2bb_trans = generate_patch_image(original_img, bbox, False, 0.0)
        img = transform(img).cuda()[None, :, :, :]
        k_value = np.array(
            [math.sqrt(cfg.bbox_real[0] * cfg.bbox_real[1] * focal[0] * focal[1] / (bbox[2] * bbox[3]))]).astype(np.float32)
        k_value = torch.FloatTensor([k_value]).cuda()[None, :]

        # forward
        with torch.no_grad():
            root_3d = model(img, k_value)  # x,y: pixel, z: root-relative depth (mm)
        img = img[0].cpu().numpy()
        root_3d = root_3d[0].cpu().numpy()

        # save output in 2D space (x,y: pixel)
        vis_img = img.copy()
        vis_img = vis_img * np.array(cfg.pixel_std).reshape(3, 1, 1) + np.array(cfg.pixel_mean).reshape(3, 1, 1)
        vis_img = vis_img.astype(np.uint8)
        vis_img = vis_img[::-1, :, :]
        vis_img = np.transpose(vis_img, (1, 2, 0)).copy()
        vis_root = np.zeros((2))
        vis_root[0] = root_3d[0] / cfg.output_shape[1] * cfg.input_shape[1]
        vis_root[1] = root_3d[1] / cfg.output_shape[0] * cfg.input_shape[0]
        cv2.circle(vis_img, (int(vis_root[0]), int(vis_root[1])), radius=5, color=(0, 255, 0), thickness=-1,
                   lineType=cv2.LINE_AA)
        root_list.append(root_3d[2])
    return root_list