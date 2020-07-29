import cv2
import numpy as np
from skimage import measure
import os
from tool import fit_square
from code25 import checkOrs25
from collections import defaultdict


# area = [x1, y1, x2, y2]
def simple_locate(im, filter_size=23, filter_threshold=1, tag_list=[], track_mode=0, area=None):
    if area is not None:
        assert len(area) == 4, 'area must have four positional parameters'
        im = im[area[1]:area[3], area[0]:area[2]]
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(gray, 1, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, filter_size,
                               filter_threshold)
    # bw = cv2.adaptiveThreshold(gray, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 3)
    # _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    # bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    label = measure.label(bw, connectivity=2)
    props = measure.regionprops(label)
    reserve_props = []
    new_bw = np.zeros_like(bw, dtype=np.uint8)
    for prop in props:
        if 500 < prop.area < 3000:
            reserve_props.append(prop)
            box = prop.bbox
            new_bw[box[0]:box[2], box[1]:box[3]] = np.maximum(new_bw[box[0]:box[2], box[1]:box[3]],
                                                              prop.image.astype(np.uint8))
    contours, hierarchy = cv2.findContours(new_bw.transpose(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    corners = []
    unrecognized_corners = defaultdict(list)
    orientations = []
    numbers = []
    values = []
    tag_center = []
    tag_length = 5
    a = np.array([1.5 / 7, 2.5 / 7, 3.5 / 7, 4.5 / 7, 5.5 / 7])
    x, y = np.meshgrid(a, a)
    trans = np.vstack((y.ravel(), x.ravel())).transpose()[None]
    SrcPointsA = np.array([[1, 1], [1, 0], [0, 0], [0, 1]], np.float32)
    for contour in contours:
        bbox = cv2.boundingRect(contour)
        contour = np.squeeze(contour)
        is_square, corner = fit_square(bbox, contour)
        if is_square:
            if np.any(corner < 0):
                continue
            for i, point in enumerate(corner):
                point = tuple(np.int32(point))
                cv2.circle(im, point, radius=5, color=(0, 255, 0), thickness=-1)
            PerspectiveMatrix = cv2.getPerspectiveTransform(SrcPointsA, np.float32(corner))
            PerspectiveImg = np.round(np.squeeze(cv2.perspectiveTransform(trans, PerspectiveMatrix)))
            # try:
            #     # value = BW[np.array(PerspectiveImg[i][:, 1], int), np.array(PerspectiveImg[i][:, 0], int)]
            #     value = np.zeros(PerspectiveImg.shape[0])
            #     i = 0
            #     for y, x in np.int32(PerspectiveImg+0.5):
            #         value[i] = int(np.round(np.mean(new_bw[x - 1:x + 2, y - 1:y + 2])))
            #         i = i + 1
            #     values.append(value)
            #     print(value)
            # except Exception:
            #     continue
            value = np.zeros(PerspectiveImg.shape[0])
            i = 0
            for y, x in np.int32(np.round(PerspectiveImg)):
                # value[i] = np.int32(np.round(new_bw[x, y]))
                value[i] = np.int32(np.round(np.mean(bw[x - 1:x + 2, y - 1:y + 2])))
                i = i + 1
            values.append(value)
            code = np.reshape(value, (tag_length, tag_length))
            pass_bin, number, _, orientation, _ = checkOrs25(code)
            if pass_bin:
                corners.append(corner)
                numbers.append(number)
                center_coordinate = np.mean(corner, axis=0)
                tag_center.append(center_coordinate)
                orientations.append(orientation)
                # orientation_coordinate = np.mean(corner[[orientation % 4, (orientation + 1) % 4]], axis=0)
                # cv2.circle(im, tuple(np.int32(orientation_coordinate)), radius=5, color=(255, 0, 0), thickness=-1)
                # orientation_coordinate = orientation_coordinate - center_coordinate
            else:
                unrecognized_corners['corner'].append(corner)
                unrecognized_corners['code'].append(code)
    # cv2.namedWindow('bumblebee', 0)
    # for i in range(len(numbers)):
    #     cv2.putText(im, str(numbers[i]), tuple(np.int32(tag_center[i])), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    #                 fontScale=2, color=(0, 0, 255), thickness=3)
    # cv2.imshow('bumblebee', im)
    # cv2.waitKey(0)
    if area is not None:
        for corner in corners:
            corner += area[:2]
        tag_center = [x + area[:2] for x in tag_center]
        for unrecognized in unrecognized_corners:
            unrecognized += area[:2]
    return numbers, orientations, corners, tag_center, unrecognized_corners


if __name__ == '__main__':
    im = cv2.imread('300.png')
    numbers_1, _, corners_1, tag_center_1, unrecognized_1 = simple_locate(im, area=[100, 1300, 2000, 2300])
    for i, number in enumerate(numbers_1):
        for corner in corners_1:
            for point in corner:
                cv2.circle(im, tuple(np.int32(point)), radius=5, color=(0, 255, 0), thickness=-1)
        cv2.putText(im, text=str(number), org=tuple(np.int32(tag_center_1[i])), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=2, color=(255, 0, 0), thickness=3)
    for corner in unrecognized_1:
        for point in corner:
            cv2.circle(im, tuple(np.int32(point)), radius=5, color=(0, 255, 0), thickness=-1)
    cv2.namedWindow('bumblebee', 0)
    cv2.imshow('bumblebee', im)
    cv2.waitKey(0)
