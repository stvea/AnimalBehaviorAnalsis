from locateCode import locate_code
import cv2
import numpy as np
from collections import defaultdict


def track_video(video, start_time, end_time, step, tag_list=[]):
    det_info = defaultdict(list)
    all_number = []
    fps = video.get(cv2.CAP_PROP_FPS)
    n_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    for i in range(int(start_time*fps), int(end_time*fps), int(step)):
        print(i)
        det_info['det_frame'].append(i)
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        success, frame = video.read()
        number, orientation, _, tag_center = locate_code(frame, threshMode=0, bradleyFilterSize=15,
                                                         bradleyThresh=3, tagList=tag_list)
        det_info['tag_label'].append(number)
        all_number.extend(number)
        det_info['orientation'].append(orientation)
        det_info['tag_center'].append(tag_center)
    if len(tag_list) == 0:
        tag_list = list(set(all_number))
    video.release()
    return det_info, tag_list


if __name__ == '__main__':
    video_name = '25s.mp4'
    video = cv2.VideoCapture(video_name)
    step = video.get(cv2.CAP_PROP_FPS)
    track_data, tag = track_video(video, 0, 25, step)
    print(tag)
