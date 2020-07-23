import numpy as np
import cv2
from scipy import signal
import warnings
from skimage import measure
from sklearn.cluster import KMeans
import cmath
from tool import point2line, direction_vector, line_intersection
import operator
from code25 import checkOrs25, code_match


# def circular_correlate(x, y):
#     length = np.int((y.shape[0] - 1) / 2)
#     x = np.pad(x, ((length, length), (0, 0)), mode='wrap')
#     return cv2.filter2D(np.array(x, float), -1, np.array(y, float))[length:-length]


def locate_code(im, **info):
    tag_length = 5
    config = {'vis': 1, 'colMode': 0, 'sizeThresh': 150, 'threshMode': 2, 'bradleyFilterSize': 15,
              'bradleyThreshold': 3, 'thresh': -1, 'robustTrack': 0, 'tagList': []}
    for x in config:
        if info.get(x) is not None:
            config[x] = info.get(x)
    vis, colMode, sizeThresh, threshMode, smP, brT, thresh, trackMode, validTagList = config['vis'], \
                                                                                      config['colMode'], config[
                                                                                          'sizeThresh'], config[
                                                                                          'threshMode'], \
                                                                                      config['bradleyFilterSize'], \
                                                                                      config['bradleyThreshold'], \
                                                                                      config['thresh'], config[
                                                                                          'robustTrack'], config[
                                                                                          'tagList']
    if len(im.shape) > 2:
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    else:
        gray = im
    if thresh > 0:
        _, BW = cv2.threshold(gray, thresh, 1, cv2.THRESH_BINARY)
    else:
        if threshMode == 0:
            BW = cv2.adaptiveThreshold(gray, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, smP, brT)
        elif threshMode == 1:
            blur = cv2.medianBlur(gray, 5)
            BW = cv2.adaptiveThreshold(blur, 1, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, smP, brT)
        elif threshMode == 2:
            # blur = cv2.GaussianBlur(gray, (5, 5), 0)
            ret, BW = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # print(np.mean(BW))
            # print(ret/255)
        elif threshMode == 3:
            blur = cv2.medianBlur(gray, 5)
            _, BW = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
        else:
            print('threshMode不能为', threshMode)
            return
    sizeThreshDef = [150, 3000]
    if type(sizeThresh) == int:
        sizeThreshDef[0] = sizeThresh
    else:
        sizeThreshDef = sizeThresh
    label, num = measure.label(BW, return_num=True, connectivity=2)
    properties = measure.regionprops(label)
    bbox, filledimage = [], []
    for propertie in properties:
        if propertie.area in range(sizeThreshDef[0], sizeThreshDef[1]):
            bbox.append(propertie.bbox)
            # print(propertie.bbox)
            filledimage.append(propertie.filled_image)
            # print(propertie.filled_image.shape)
            # print(propertie.filled_image)
    if len(bbox) == 0:
        print('No sufficiently large what regions detected - try changing threshMode for binary '
              'image or tag size (sizeThresh)')
        return [], [], []
    corners = []
    for i in range(len(bbox)):
        # print(bbox[i])
        # cv2.rectangle(im, (bbox[i][1], bbox[i][0]), (bbox[i][3], bbox[i][2]), (0, 0, 255), 2)
        try:
            isq, corner = fitquad(bbox[i], np.array(filledimage[i], np.uint8))
        except Exception:
            continue
        if isq:
            corners.append(corner)
    if len(corners) == 0:
        print('No potentially valid tag regions found')
        return [], [], []
    a = np.array([5.5 / 7, 4.5 / 7, 3.5 / 7, 2.5 / 7, 1.5 / 7])
    x, y = np.meshgrid(a, a)
    trans = np.vstack((y.ravel(), x.ravel())).transpose()[:, None]
    # print(np.vstack((y.ravel(), x.ravel())).transpose())
    SrcPointsA = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], np.float32)
    PerspectiveImg = []
    for i in range(len(corners)):
        PerspectiveMatrix = cv2.getPerspectiveTransform(SrcPointsA, np.array(corners[i][:, ::-1], np.float32))
        PerspectiveImg.append(np.round(np.squeeze(cv2.perspectiveTransform(trans, PerspectiveMatrix))))
    orientations = []
    numbers = []
    values = []
    tag_center = []
    for i in range(len(PerspectiveImg)):
        # print(corners[i][:, ::-1])
        try:
            # value = BW[np.array(PerspectiveImg[i][:, 1], int), np.array(PerspectiveImg[i][:, 0], int)]
            value = np.zeros(PerspectiveImg[i].shape[0])
            for j in range(PerspectiveImg[i].shape[0]):
                y, x = np.array(PerspectiveImg[i][j]+0.5, int)
                value[j] = int(np.round(np.mean(BW[x-1:x+2, y-1:y+2])))
            values.append(value)
        except Exception:
            corners.pop(len(corners)-len(PerspectiveImg)+i)
            continue
    if trackMode == 0:
        for i in range(len(corners))[::-1]:
            code = np.reshape(values[i], (tag_length, tag_length))
            # print(code)
            code = code[:, ::-1]
            pass_bin, number, _, orientation, _ = checkOrs25(code)
            if pass_bin:
                if len(validTagList):
                    if number not in validTagList:
                        corners.pop(i)
                        continue
                numbers.append(number)
                center_coordinate = np.mean(corners[i], axis=0)
                tag_center.append(center_coordinate)
                orientation_coordinate = np.mean(corners[i][[orientation % 4, (orientation + 1) % 4]], axis=0)
                orientation_coordinate = orientation_coordinate - center_coordinate
                orientation_polar = cmath.polar(orientation_coordinate[0] + orientation_coordinate[1]*1j)
                orientations.append(orientation_polar[1])
            else:
                corners.pop(i)
    elif trackMode == 1:
        if len(validTagList) == 0:
            print('使用此方法，validTagList不能为空')
            exit()
        for i in range(len(corners))[::-1]:
            code = np.reshape(values[i], (tag_length, tag_length))
            code = code[:, ::-1]
            pass_bin, number, orientation = code_match(code, validTagList)
            if pass_bin >= 25 / 25:
                numbers.append(number)
                center_coordinate = np.mean(corners[i], axis=0)
                tag_center.append(center_coordinate)
                orientation_coordinate = np.mean(corners[i][[orientation % 4, (orientation + 1) % 4]], axis=0)
                orientation_coordinate = orientation_coordinate - center_coordinate
                orientation_polar = cmath.polar(orientation_coordinate[0] + orientation_coordinate[1] * 1j)
                orientations.append(orientation_polar[1])
            else:
                corners.pop(i)

    # if vis == 1:
    #     cv2.namedWindow('image', 0)
    #     for i in range(len(corners)):
    #         cv2.circle(im, tuple(np.array(corners[i][0], int)[::-1]), 2, (0, 255, 0), 4)
    #         cv2.circle(im, tuple(np.array(corners[i][1], int)[::-1]), 3, (0, 255, 0), 4)
    #         cv2.circle(im, tuple(np.array(corners[i][2], int)[::-1]), 4, (0, 255, 0), 4)
    #         cv2.circle(im, tuple(np.array(corners[i][3], int)[::-1]), 5, (0, 255, 0), 4)
    #     if colMode == 1:
    #         cv2.imshow('image', gray)
    #     elif colMode == 0:
    #         cv2.imshow('image', BW*255)
    #     elif colMode == 2:
    #         cv2.imshow('image', im)
    #     cv2.waitKey(0)
    return numbers, orientations, corners, tag_center


def fitquad(bbox, mask):
    isQuad = False
    corner = np.zeros((4, 2))
    cls = 4
    # print(mask.shape)
    # print(mask)
    mask = np.pad(mask, ((3, 3), (3, 3)), mode='constant')
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # 返回指定形状和尺寸的结构元素
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = mask[3:-3, 3:-3]
    contours, hierarchy = cv2.findContours(mask.transpose(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = np.squeeze(contours[0])
    # print(contour.shape)
    # print(contour)
    kernelSize = np.floor(np.min(mask.shape) / 3).astype(int)
    kernel = np.convolve(np.array([-1, 0, 1], float) / 2,
                         np.squeeze(cv2.getGaussianKernel(kernelSize, kernelSize / 6)))[:, None]
    # print(kernel)
    gradients = signal.convolve2d(contour, kernel, boundary='wrap', mode='same')  # 高斯第一平滑导数
    # print(gradients.shape)
    # print(gradients)
    # seedIdx1 = np.floor(np.linspace(0, gradients.shape[0], 5))
    # seedIdx2 = seedIdx1 + np.floor((seedIdx1[1]-seedIdx1[0])/2)
    # seedIdx2 = np.array(seedIdx2, np.int)
    kmean = KMeans(n_clusters=cls, max_iter=100)
    kmean.fit(gradients)
    label = kmean.labels_
    points = []
    for i in range(cls):
        points.append(contour[label == i])
    points_length = [points[i].shape[0] for i in range(cls)]
    if min(points_length) < max(points_length) / 4.0:
        return isQuad, corner
    line = np.zeros((cls, 2))
    rcond = np.finfo(np.float32).eps
    warnings.simplefilter('ignore', np.RankWarning)
    for i in range(cls):
        if len(points[i]) < 3:
            return isQuad, corner
        line[i] = np.polyfit(points[i][:, 0]+rcond, points[i][:, 1]+rcond, deg=1)
    # print(line)
    maxIter = 6
    step = 0
    isConverged = False
    isDegenerate = False
    minPtsPrClstr = gradients.shape[0] / 4 * 0.5
    while step < maxIter and not isConverged and not isDegenerate:
        distances = []
        for i in range(cls):
            distances.append(point2line(contour, line[i]))
        distances = np.vstack(distances)
        # print(distances.shape)
        minind = np.argsort(distances, axis=0)[0]
        new_points = []
        for i in range(cls):
            new_points.append(contour[minind == i])
            if new_points[i].shape[0] < minPtsPrClstr:
                isDegenerate = True
        # print(label)
        # print(minind)
        isConverged = all(operator.eq(label, minind))
        # print(isConverged)
        if not isConverged:
            points = new_points
            label = minind
            for i in range(cls):
                line[i] = np.polyfit(points[i][:, 0]+rcond, points[i][:, 1]+rcond, deg=1)
        step += 1
    if not isConverged or isDegenerate:
        return isQuad, corner
    vector = direction_vector(line)
    product = np.sum(vector[0] * vector[1:4], axis=1)
    ind = np.argsort(product)
    if product[ind[2]] < 0.85 and product[ind[1]] - product[ind[0]] > 0.15:
        return isQuad, corner
    corner[0] = line_intersection(line[0], line[ind[0] + 1])
    corner[1] = line_intersection(line[ind[0] + 1], line[ind[2] + 1])
    corner[2] = line_intersection(line[ind[1] + 1], line[ind[2] + 1])
    corner[3] = line_intersection(line[0], line[ind[1] + 1])
    # print(corner)
    midToCorner = corner - (np.array(mask.shape)) / 2
    r = np.zeros(cls)
    theta = np.zeros(cls)
    for i in range(cls):
        [a, b] = cv2.cartToPolar(midToCorner[i, 0], midToCorner[i, 1], angleInDegrees=False)
        r[i] = a[0]
        theta[i] = b[0] if b[0] < 3.1415 else b[0] - 3.1415 * 2
    if any(r > np.sqrt(sum(np.array(mask.shape) ** 2)) / 2 * 1.1):
        return isQuad, corner
    # print(theta)
    ind = np.argsort(theta)
    corner = corner[ind]
    # print(corner)
    corner = corner + bbox[0:2]
    isQuad = True
    return isQuad, corner


if __name__ == '__main__':
    im = cv2.imread('picture/000720.png')
    number, orientation, corners, tag_center = locate_code(im, threshMode=0, bradleyFilterSize=15, bradleyThresh=3)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(len(corners)):
        for j in range(4):
            cv2.circle(im, tuple(np.array(corners[i][j], int)[::-1]), 6, (0, 255, 0), -1)
        center = np.round(tag_center[i]).astype(int)
        cv2.putText(im, str(number[i]), (center[1], center[0]), font, 3, (255, 0, 0), 4)
    cv2.namedWindow('image', 0)
    cv2.imshow('image', im)
    cv2.waitKey(0)
    # print(number, orientation, corners)
