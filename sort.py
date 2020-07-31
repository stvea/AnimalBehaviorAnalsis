import numpy as np
from tool import polygon_iou, code_match
from scipy.optimize import linear_sum_assignment
import cv2
from simple_locate import simple_locate
import pickle
import os
import time
from collections import defaultdict


class cornerTracker(object):
    count = 0

    def __init__(self, number, corners, orientation, pos_frame):
        self.time_since_update = 0
        self.number = number
        self.history_corner = [corners]
        self.history_orientation = [orientation]
        self.pos_frames = [pos_frame]
        cornerTracker.count += 1
        self.hit_streak = 0
        self.time_since_update = 0

    def update(self, corners, orientation, pos_frame):
        self.hit_streak += 1
        self.time_since_update = 0
        self.history_corner.append(corners)
        self.history_orientation.append(orientation)
        self.pos_frames.append(pos_frame)

    def predict(self):
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


def get_detect_info(file_name, SystemInfo):
    with open(file_name, 'rb') as fr:
        mul_tracker = pickle.load(fr)
        SystemInfo.detect_all_number = []
        for i in range(int(SystemInfo.detect_set_start_time * SystemInfo.video_fps),
                       int(SystemInfo.detect_set_end_time * SystemInfo.video_fps) + 1, int(SystemInfo.detect_set_step)):
            SystemInfo.detect_info['detect_frame'].append(i)
            number, orientation, tag_center = [], [], []
            for tracker in mul_tracker.trackers:
                if i in tracker.pos_frames:
                    idx = tracker.pos_frames.index(i)
                    number.append(tracker.number)
                    orientation.append(tracker.history_orientation[idx])
                    tag_center.append(np.mean(tracker.history_corner[idx], axis=0))
            SystemInfo.detect_info['tag_label'].append(number)
            SystemInfo.detect_info['orientation'].append(orientation)
            SystemInfo.detect_info['tag_center'].append(tag_center)


class Sort(object):
    def __init__(self, max_age=50, min_hits=1, step=1, area=[]):
        self.max_age = max_age
        self.min_hits = min_hits
        self.trackers = []
        self.frame_count = 0
        self.frame_pos = 0
        self.numbers = []
        self.history = defaultdict(list)
        self.step = step
        self.area = area

    def update(self, frame):
        numbers, orientation, corners, tag_center, unrecognized = simple_locate(frame, area=self.area)
        for tracker in self.trackers:
            tracker.predict()
        for i, number in enumerate(numbers):
            if number in self.numbers:
                trk = [x for x in self.trackers if x.number == number]
                trk[0].update(corners[i], orientation[i], self.frame_pos)
            else:
                self.numbers.append(number)
                self.trackers.append(cornerTracker(number, corners[i], orientation[i], self.frame_pos))
        trks = []
        for trk in self.trackers:
            if 0 < trk.time_since_update*self.step < self.max_age:
                trks.append(trk)
        dets = unrecognized['corners']
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(dets, trks)
        # update matched trackers with assigned detections
        for m in matched:
            similarity, orientation = code_match(unrecognized['code'][m[0]], trks[m[1]].number)
            if similarity > 0.75:
                trks[m[1]].update(dets[m[0]], orientation, self.frame_pos)
            else:
                unmatched_dets.append(m[0])
        if len(unmatched_dets) > 0:
            self.history['frame_pos'].append(self.frame_pos)
            self.history['corners'].append(dets[unmatched_dets])
        self.frame_count += 1
        self.frame_pos += self.step


if __name__ == '__main__':
    filename = '25s.mp4'
    step = 40
    save_file = 'detection_' + os.path.splitext(filename)[0] + '.pkl'
    video = cv2.VideoCapture(filename)
    success, frame = video.read()
    print(video.get(cv2.CAP_PROP_FRAME_COUNT))
    mot_tracker = Sort(step=step)
    total_time = 0.0
    total_frames = 0
    tic = time.time()
    while success:
        print(total_frames*step)
        mot_tracker.update(frame)
        total_frames += 1
        video.set(cv2.CAP_PROP_POS_FRAMES, total_frames*step)
        success, frame = video.read()
    video.release()
    # with open(save_file, 'wb') as f:
    #     pickle.dump(mot_tracker, f)
    # toc = time.time()
    # total_time = toc-tic
    # print(total_time)
