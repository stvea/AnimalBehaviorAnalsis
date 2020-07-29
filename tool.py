import numpy as np
import cv2
from scipy import signal
from sklearn.cluster import KMeans
import warnings
import math
from code25 import number_to_code


def fit_square(bbox, contour):
    contour = contour - np.array(bbox[0:2])
    is_square = False
    corner = np.zeros((4, 2))
    cls = 4
    kernel_size = np.int32(np.min(bbox[2:]) / 3)
    kernel = np.convolve(np.array([-1, 0, 1], np.float32) / 2,
                         np.squeeze(cv2.getGaussianKernel(kernel_size, kernel_size / 6)))[:, None]
    gradients = signal.convolve2d(contour, kernel, boundary='wrap', mode='same')  # 高斯第一平滑导数
    k_mean = KMeans(n_clusters=cls, random_state=0).fit(gradients)
    label = k_mean.labels_
    points = []
    for i in range(cls):
        points.append(contour[label == i])
    points_length = [points[i].shape[0] for i in range(cls)]
    if min(points_length) < max(points_length) / 4.0:
        return is_square, None
    line = np.zeros((cls, 2))
    eps = np.finfo(np.float32).eps
    warnings.simplefilter('ignore', np.RankWarning)
    for i in range(cls):
        if len(points[i]) < 3:
            return is_square, corner
        line[i] = np.polyfit(points[i][:, 0]+eps, points[i][:, 1]+eps, deg=1)
    max_iterate = 160
    step = 0
    is_converged = False
    is_degenerate = False
    num_min_cluster = gradients.shape[0] / 4 * 0.25
    while step < max_iterate and not is_converged and not is_degenerate:
        distances = []
        for i in range(cls):
            distances.append(point2line(contour, line[i]))
        distances = np.vstack(distances)
        min_ind = np.argsort(distances, axis=0)[0]
        new_points = []
        for i in range(cls):
            new_points.append(contour[min_ind == i])
            if new_points[i].shape[0] < num_min_cluster:
                is_degenerate = True
        is_converged = all(np.equal(label, min_ind))
        if not is_converged and not is_degenerate:
            points = new_points
            label = min_ind
            for i in range(cls):
                line[i] = np.polyfit(points[i][:, 0]+eps, points[i][:, 1]+eps, deg=1)
        step += 1
    if not is_converged or is_degenerate:
        return is_square, None
    vector = direction_vector(line)
    product = np.sum(vector[0] * vector[1:4], axis=1)
    ind = np.argsort(product)
    product = product[ind]
    if product[2] < 0.9 or abs(product[0]) > 0.15 or abs(product[1]) > 0.15:
        return is_square, None
    corner[0] = line_intersection(line[0], line[ind[0] + 1])
    corner[1] = line_intersection(line[ind[0] + 1], line[ind[2] + 1])
    corner[2] = line_intersection(line[ind[1] + 1], line[ind[2] + 1])
    corner[3] = line_intersection(line[0], line[ind[1] + 1])
    center = np.array([(bbox[2]-1)/2, (bbox[3]-1)/2])
    corner_to_center = corner - center
    radius, theta = cv2.cartToPolar(corner_to_center[:, 0], corner_to_center[:, 1], angleInDegrees=False)
    if any(radius.ravel() > np.sqrt(sum(np.array(bbox[2:]) ** 2)) / 2 * 1.1):
        return is_square, None
    ind = np.argsort(theta.ravel())
    corner = corner[ind]
    is_square = True
    return is_square, np.flip(corner+np.array(bbox[0:2]), axis=1)


def point2line(point, line):
    distance = np.abs(line[0]*point[:, 0]-point[:, 1]+line[1])/np.sqrt(line[0]**2+1)
    return distance


def direction_vector(line):
    x = line[:, 0]/np.sqrt(line[:, 0]**2+1)
    y = 1/np.sqrt(line[:, 0]**2+1)
    return np.vstack((x, y)).transpose()


def line_intersection(line1, line2):
    x = (line2[1]-line1[1])/(line1[0]-line2[0])
    y = (line1[0]*line2[1]-line1[1]*line2[0])/(line1[0]-line2[0])
    return np.array([x, y])


def polygon_iou(im1_shape, im2_shape, poly1, poly2):
    im1 = np.zeros(im1_shape, dtype=np.uint8)
    im2 = np.zeros(im2_shape, dtype=np.uint8)
    filled_im1 = cv2.fillPoly(im1, [poly1], 255)
    filled_im2 = cv2.fillPoly(im2, [poly2], 255)
    or_area = cv2.bitwise_or(filled_im1, filled_im2)
    and_area = cv2.bitwise_and(filled_im1, filled_im2)
    iou = np.sum(np.float32(np.greater(and_area, 0)))/np.sum(np.float32(np.greater(or_area, 0)))
    return iou


def code_match(raw_code, number):
    real_code = number_to_code(number)
    match = np.zeros(4)
    for i in range(4):
        variant_code = np.rot90(raw_code, i+1)
        match[i] = np.sum(variant_code == code)/np.prod(raw_code.shape)
    return np.max(match), np.argmax(match)


if __name__ == '__main__':
    line1 = [1, 2]
    line2 = [4, 4]
    print(line_intersection(line1, line2))