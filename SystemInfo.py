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

    video_label_size = []
    video_label_hint_size = []

    video_opened_url = None
    video_is_opened = False
    video_is_play = False
    video_is_detect = False
    video_fps = 12
    video_time = 0
    video_now_fps = 0
    video_now_time = 0
    video_total_fps = 0

    # 0:show video 1:detect result
    video_mode = 0

    # [x0,y0,x1,y1]
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
    default_dir = ''
    main_view = None

    operate_menus = [['视频操作', '查看视频信息'], ['检测设置', '标注区域', '视频范围', '比例尺'], ['结果分析', '结果预览', '数据导出', '数据预览']]

    def log(TAG, msg):
        SystemInfo.main_view.status.showMessage(
            "[{}] [{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), TAG, msg), 1000)
        print("[{}] [{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), TAG, msg))

    def read(config, section):
        SystemInfo.detect_step = config.getint(section, 'step')
        SystemInfo.detect_set_start_time = config.get(section, 'startTime')
        SystemInfo.detect_set_end_time = config.get(section, 'endTime')
        SystemInfo.detect_area = [config.getint(section, 'x1'), config.getint(section, 'y1'),
                                  config.getint(section, 'x2'), config.getint(section, 'y2')]

    def modified(config_file):
        pass

    def write(config, section, file_name):  # 创建一个新的配置文件
        config.add_section(section)
        config.set(section, 'startTime', str(SystemInfo.detect_set_start_time))
        config.set(section, 'endTime', str(SystemInfo.detect_set_end_time))
        config.set(section, 'x1', str(SystemInfo.detect_area[0]))
        config.set(section, 'y1', str(SystemInfo.detect_area[1]))
        config.set(section, 'x2', str(SystemInfo.detect_area[2]))
        config.set(section, 'y2', str(SystemInfo.detect_area[3]))
        with open(file_name, 'w+') as f:
            config.write(f)

    def get(system_config_file):
        if os.path.exists(system_config_file):
            config = configparser.ConfigParser()
            config.read(system_config_file)
            SystemInfo.default_dir = config.get('dir', 'default_dir')
