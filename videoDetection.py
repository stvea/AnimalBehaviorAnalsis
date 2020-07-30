from simple_locate import simple_locate
import os
import cv2
import numpy as np

if __name__ == '__main__':
    count1 = 0
    count2 = 0
    filename = 'bumblebee.mp4'
    video = cv2.VideoCapture(filename)
    fps = np.int32(video.get(cv2.CAP_PROP_FPS))
    width, height = np.int32(video.get(cv2.CAP_PROP_FRAME_WIDTH)), np.int32(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    write_video = cv2.VideoWriter('detection_' + filename, fourcc, fps, (width, height))
    success, frame = video.read()
    count = 0
    while success:
        numbers, orientation, corners, tag_centers, unrecognized = simple_locate(frame, filter_size=23,
                                                                                 filter_threshold=-1)
        unrecognized_corners = unrecognized['corner']
        for i, number in enumerate(numbers):
            cv2.putText(frame, str(number), org=tuple(np.int32(tag_centers[i])), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=2, color=(255, 0, 0), thickness=3)
        for corner in corners:
            for point in corner:
                cv2.circle(frame, tuple(np.int32(point)), radius=5, color=(0, 255, 0), thickness=-1)
        for unrecognized_corner in unrecognized_corners:
            for point in unrecognized_corner:
                cv2.circle(frame, tuple(np.int32(point)), radius=4, color=(0, 255, 0), thickness=-1)
        count1 = count1 + len(numbers)
        count2 = count2 + len(unrecognized_corners)
        write_video.write(frame)
        count += 1
        print(count)
        success, frame = video.read()
    print(count1, count2)
    print(video.isOpened())
    write_video.release()