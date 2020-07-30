from collections import defaultdict
import time
import os
import configparser

class SystemInfo:
    video_name = []
    # video's cache list index is the frame
    video_cache = []
    video_is_cached = False
    video_cache_fps = 0
    video_size = []

    video_label_size =[]
    video_label_hint_size = []

    video_opened_url = None
    video_is_opened = False
    video_isPlay = False
    video_fps = 12
    video_time = 0
    video_now_fps = 0
    video_now_time = 0
    video_total_fps = 0

    # 0:show video 1:detect result
    video_mode = 0

    #[x0,y0,x1,y1]
    detect_area = []
    detect_area_show = False
    detect_area_flag = False

    detect_scale = []
    detect_scale_label = 0
    detect_scale_real = 0
    detect_scale_ratio = 0

    detect_set_start_time = 0
    detect_set_end_time = 0
    detect_set_step = 1
    detect_step = 1
    detect_info = defaultdict(list)
    detect_all_number = []

    video = None
    video_thread = None

    main_view = None

    operate_menus = [['视频操作', '查看视频信息'], ['检测设置', '标注区域', '视频范围','比例尺'], ['结果分析', '结果预览', '数据导出', '数据预览']]

    def log(TAG,msg):
        SystemInfo.main_view.status.showMessage('"[{}] [{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),TAG,msg)',1000)
        print("[{}] [{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),TAG,msg))

    def read(config_file):
        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            SystemInfo.video_opened_url = config.get('video', 'url')
            SystemInfo.detect_step = config.getint('detectSet', 'step')
            SystemInfo.detect_set_start_time = config.get('detectSet', 'startTime')
            SystemInfo.detect_set_end_time = config.get('detectSet', 'endTime')
            # SystemInfo.detect_area = [config.getint('detectSet', 'x1'), config.getint('detectSet', 'y1'),
            #                           config.getint('detectSet', 'x2'), config.getint('detectSet', 'y2')]

    def modified(config_file):
        pass

    def write(config_file):                  # 创建一个新的配置文件
        config = configparser.ConfigParser()
        config.add_section('video')
        config.add_section('detectSet')
        config.set('video', 'url', SystemInfo.video_opened_url)
        SystemInfo.detect_step = config.getint('detectSet', 'step')
        config.set('detectSet', 'startTime', str(SystemInfo.detect_set_start_time))
        config.set('detectSet', 'endTime', str(SystemInfo.detect_set_end_time))
        # config.set('detectSet', 'x1', str(SystemInfo.detect_area[0]))
        # config.set('detectSet', 'y1', str(SystemInfo.detect_area[1]))
        # config.set('detectSet', 'x2', str(SystemInfo.detect_area[2]))
        # config.set('detectSet', 'y2', str(SystemInfo.detect_area[3]))