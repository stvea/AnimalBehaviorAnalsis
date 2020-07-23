import cv2
import os
import numpy as np
# from locateCode import locate_code
from scipy import signal
if __name__ == '__main__':
    a = np.arange(12).reshape(6, 2).astype(np.float64)
    print(a.dtype)
    b = np.array([[1.0], [2.0], [3.0]])
    print(b.dtype)
    c = signal.convolve2d(a, b, boundary='wrap', mode='same')
    print(a)
    print(b)
    print(c)