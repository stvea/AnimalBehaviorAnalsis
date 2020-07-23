import cv2
import os
if __name__ == '__main__':
    out_dir = 'picture'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    video = cv2.VideoCapture('25s.mp4')
    n_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    for i in range(0, n_frames, fps):
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        success, frame = video.read()
        cv2.imshow('bumblebee', frame)
        cv2.waitKey(0)
        filename = os.path.join(out_dir, '{:06}.png'.format(i))
        cv2.imwrite(filename, frame)