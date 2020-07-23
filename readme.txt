trackVideo.py
          track_video(video, start_time, end_time, step, tag_list=[])
          参数说明：
          video 待检测的视频，cv2.VideoCapture对象.
          start_time 视频检测起始时间，单位s
          end_time  视频检测结束时间，单位s
          step 相隔多少帧检测一张图片
          tag_list 有效的标签列表，即视频中含有哪些二维码，list对象
          det_info 字典，包含了视频检测的所有信息
这个函数需要看一下，就20行左右，就是每帧的检测结果（下面的函数），整合在一起。


核心功能函数
locateCode.py中的locate_code函数
           locate_code(frame, threshMode=0, bradleyFilterSize=15, bradleyThresh=3, tagList=tag_list)
           参数说明：
           frame 待处理的图像/帧
           threshMode，bradleyFilterSize，bradleyThresh不用管，使用我这里默认的参数即可
           tagList 有效的标签列表，如上

           返回值
           numbers, orientations, corners, tag_center
           numbers 图像/帧中检测到的二维码id，list对象
           orientations 图像/帧中二维码的方向，list对象
           corners 图像/帧中二维码的四个顶点坐标， array llist对象
           tag_center 二维码的中心坐标，array list对象
          
            一张图像中含有多个二维码，在这四个返回值中位置是对应的。即四个返回值有相同的长度。
            numbers[i], orientations[i],corners[i]（4x2array顶点坐标）,tag_center[i]（1x2array，中心坐标）
            分别表示第i个二维码的id，方向，四顶点坐标，中心坐标
            直接运行locateCode.py能看到图片300.png的检测效果
