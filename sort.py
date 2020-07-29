import numpy as np
from tool import polygon_iou, code_match
from scipy.optimize import linear_sum_assignment
import cv2
from simple_locate import simple_locate
import pickle
import os
import time


class cornerTracker(object):
    count = 0

    def __init__(self, number, corners, orientation, pos_frame):
        self.time_since_update = 0
        self.number = number
        self.history_corner = [corners]
        self.history_orientation = [orientation]
        self.pos_frames = [pos_frame]
        cornerTracker.count += 1
        self.hits = 0
        self.hit_streak = 0
        self.time_since_update = 0
        self.age = 0

    def update(self, corners, orientation, pos_frame):
        self.hits += 1
        self.hit_streak += 1
        self.time_since_update = 0
        self.history_corner.append(corners)
        self.history_orientation.append(orientation)
        self.pos_frames.append(pos_frame)

    def predict(self):
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        return self.history_corner[-1]


def associate_detections_to_trackers(detections, trackers, iou_threshold=0.5):

    if len(trackers) == 0:
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0, 5), dtype=int)
    iou_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)

    for d, det in enumerate(detections):
        for t, trk in enumerate(trackers):
            iou_matrix[d, t] = polygon_iou(det, trk)

    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            matched_indices = zip(linear_sum_assignment(-iou_matrix))
    else:
        matched_indices = np.empty(shape=(0, 2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if d not in matched_indices[:, 0]:
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if t not in matched_indices[:, 1]:
            unmatched_trackers.append(t)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1, 2))
    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class Sort(object):
    def __init__(self, max_age=50, min_hits=1):
        self.max_age = max_age
        self.min_hits = min_hits
        self.trackers = []
        self.frame_count = 0
        self.numbers = []
        self.history = []

    def update(self, frame):
        numbers, orientation, corners, tag_center, unrecognized = simple_locate(frame)
        for tracker in self.trackers:
            tracker.predict()
        for i, number in enumerate(numbers):
            if number in self.numbers:
                trk = [x for x in self.trackers if x.number == number]
                trk[0].update(corners[i], orientation[i], self.frame_count)
            else:
                self.numbers.append(number)
                self.trackers.append(cornerTracker(number, corners[i], orientation[i], self.frame_count))
        trks = []
        for trk in self.trackers:
            if 0 < trk.time_since_update < self.max_age:
                trks.append(trk)
        dets = unrecognized['corners']
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(dets, trks)
        # update matched trackers with assigned detections
        for m in matched:
            similarity, orientation = code_match(unrecognized['code'][m[0]], trks[m[1]].number)
            if similarity > 0.75:
                trks[m[1]].update(dets[m[0]], orientation, self.frame_count)
            else:
                unmatched_dets.append(m[0])
        if len(unmatched_dets) > 0:
            self.history.append(dets[unmatched_dets])
        else:
            self.history.append([])
        self.frame_count += 1


if __name__ == '__main__':
    filename = '25s.mp4'
    save_file = 'detection_' + os.path.splitext(filename)[0] + '.pkl'
    video = cv2.VideoCapture(filename)
    success, frame = video.read()
    mot_tracker = Sort()
    total_time = 0.0
    total_frames = 0
    tic = time.time()
    while success:
        total_frames += 1
        print(total_frames)
        mot_tracker.update(frame)
        success, frame = video.read()
    video.release()
    with open(save_file, 'wb') as f:
        pickle.dump(mot_tracker, f)
    toc = time.time()
    total_time = toc-tic
    print(total_time)
