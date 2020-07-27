from collections import defaultdict


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
    detect_area_flag = False
    detect_set_start_time = 0
    detect_set_end_time = 0
    detect_set_step = 20
    detect_step = 1
    detect_info = defaultdict(list)
    detect_all_number = []

    video = None
    video_thread = None
