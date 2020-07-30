import pickle
import cv2
import numpy as np
from sort import Sort, cornerTracker

with open('detection.pkl', 'rb') as f:
    mot_tracker = pickle.load(f)
filename = '25s.mp4'
video = cv2.VideoCapture(filename)
fps = np.int32(video.get(cv2.CAP_PROP_FPS))
width, height = np.int32(video.get(cv2.CAP_PROP_FRAME_WIDTH)), np.int32(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
write_video = cv2.VideoWriter('detection.mp4', fourcc, fps, (width, height))
pos_frame = 0
success, frame = video.read()
while success:
    print(pos_frame)
    for tracker in mot_tracker.trackers:
        if pos_frame in tracker.pos_frames:
            i = tracker.pos_frames.index(pos_frame)
            center = np.mean(tracker.history_corner[i], axis=0)
            for point in tracker.history_corner[i]:
                cv2.circle(frame, tuple(np.int32(point)), radius=5, color=(0, 255, 255), thickness=-1)
            cv2.putText(frame, str(tracker.number), org=tuple(np.int32(center)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2,
                        color=(255, 0, 0), thickness=3)
    write_video.write(frame)
    success, frame = video.read()
    pos_frame += 1
video.release()
write_video.release()