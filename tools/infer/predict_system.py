
import os
import sys
from socketserver import BaseRequestHandler,ThreadingTCPServer
import threading
import struct

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

import cv2
import copy
import numpy as np
import time
from PIL import Image
import tools.infer.utility as utility
import tools.infer.predict_rec as predict_rec
import tools.infer.predict_det as predict_det
import tools.infer.predict_cls as predict_cls
from ppocr.utils.utility import get_image_file_list, check_and_read_gif
from ppocr.utils.logging import get_logger
from tools.infer.utility import draw_ocr_box_txt

logger = get_logger()

class TextSystem(object):
    def __init__(self, args):
        self.text_detector = predict_det.TextDetector(args)
        self.text_recognizer = predict_rec.TextRecognizer(args)
        self.use_angle_cls = args.use_angle_cls
        self.drop_score = args.drop_score
        if self.use_angle_cls:
            self.text_classifier = predict_cls.TextClassifier(args)

    def get_rotate_crop_image(self, img, points):
        '''
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        '''
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3])))
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2])))
        pts_std = np.float32([[0, 0], [img_crop_width, 0],
                              [img_crop_width, img_crop_height],
                              [0, img_crop_height]])
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M, (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC)
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def print_draw_crop_rec_res(self, img_crop_list, rec_res):
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite("./output/img_crop_%d.jpg" % bno, img_crop_list[bno])
            logger.info(bno, rec_res[bno])

    def __call__(self, img):
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img)
        # logger.info("dt_boxes num : {}, elapse : {}".format(
        #     len(dt_boxes), elapse))
        if dt_boxes is None:
            return None, None
        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        if self.use_angle_cls:
            img_crop_list, angle_list, elapse = self.text_classifier(
                img_crop_list)
            # logger.info("cls num  : {}, elapse : {}".format(
            #     len(img_crop_list), elapse))

        rec_res, elapse = self.text_recognizer(img_crop_list)
        # logger.info("rec_res num  : {}, elapse : {}".format(
        #     len(rec_res), elapse))
        # self.print_draw_crop_rec_res(img_crop_list, rec_res)
        filter_boxes, filter_rec_res = [], []
        for box, rec_reuslt in zip(dt_boxes, rec_res):
            text, score = rec_reuslt
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_reuslt)
        return filter_boxes, filter_rec_res


def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and \
                (_boxes[i + 1][0][0] < _boxes[i][0][0]):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes

def box_y(box_list):
    box_y_top , box_y_buttom = box_list[0][1],box_list[2][1]
    box_x_left,box_x_right = box_list[0][0],box_list[1][0]
    return (box_x_left,box_x_right,box_y_top,box_y_buttom)

def main(args):
    img_dir = os.listdir(args.image_dir)
    for dir in img_dir:
        image_file_list = get_image_file_list('./imgs/{}'.format(dir))
        text_sys = TextSystem(args)
        is_visualize = True
        font_path = args.vis_font_path
        drop_score = args.drop_score
        epoch,win_num = 0,0
        for image_file in image_file_list:
            img, flag = check_and_read_gif(image_file)
            if not flag:
                img = cv2.imread(image_file)
            if img is None:
                logger.info("error in loading image:{}".format(image_file))
                continue
            starttime = time.time()
            dt_boxes, rec_res = text_sys(img)
            # print(rec_res)
            res_update=[]
            dt_update = []
            for i in range(len(dt_boxes)):
                box = dt_boxes[i]
                if box_y(box)[2]>250 and box_y(box)[3]<420 and box_y(box)[1]<650 and box_y(box)[0]>300:
                    res_update.append(rec_res[i])
                    dt_update.append(box)
            rec_res=res_update
            dt_boxes=dt_update
            # elapse = time.time() - starttime
            # logger.info("Predict time of %s: %.3fs" % (image_file, elapse))
            rec_res = rec_res[0][0] if len(rec_res)==1 else rec_res[0][0]+rec_res[1][0]
            logger.info("游戏结果：%s" % (rec_res))
            if rec_res == '0连胜':
                pass
            else:
                win_num += 1
            epoch += 1
        print(win_num/epoch)
        with open('win_count.txt','a',encoding='utf-8') as f:
            f.write('游戏局数：%s,胜利局数：%s,本次胜率：%s'%(epoch,win_num,win_num/epoch))
            f.write('\n')
        return rec_res



if __name__ == "__main__":

    rec_res = main(utility.parse_args())
    # print(rec_res)






