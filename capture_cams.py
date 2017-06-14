import time
import re
import archiver
import camera
import sys

def create_cam_dict(filename):
    cam_dict = {}

    f = open(filename, 'r')
    f.readline() # get rid of the header line
    lines = f.readlines()

    for line in lines:
        m = re.search(r"^(\d+),.*,.*,.*,.*,([\d:\.]+),([\d:\.]+)", line)
        if m:
            cam_id = m.group(1)
            start_time = convert_time(m.group(2))
            end_time = convert_time(m.group(3))
            if (start_time is not None and end_time is not None):
                duration = end_time - start_time
                # the last element in cam_dict[cam_id]
                # is whether the script has taken from the camera
                cam_dict[cam_id] = [start_time, end_time, duration, False]

    return cam_dict

def create_cam_list(filename):
    cam_list = []

    f = open(filename, 'r')
    f.readline() # get rid of the header line
    lines = f.readlines()

    min_start = -1
    max_end = -1
    for line in lines:
        m = re.search(r"^(\d+),.*,.*,.*,.*,([\d:\.]+),([\d:\.]+)", line)
        if m:
            cam_id = int(m.group(1))
            start_time = convert_time(m.group(2))
            end_time = convert_time(m.group(3))
            if (start_time < min_start or min_start == -1):
                min_start = start_time
            if (end_time > max_end):
                max_end = end_time
            cam_list.append(cam_id)

    return [cam_list, min_start, max_end]

def convert_time(time_str):
    m = re.search(r"^(\d{2}):(\d{2}):(\d{2})", time_str)
    if m:
        hours = int(m.group(1))
        mins = int(m.group(2))
        secs = int(m.group(3))
        return (hours * 3600 + mins * 60 + secs)

    # if m is None
    raise ValueError("time string not in following format: 'hh:mm:ss'")

def get_time():
    cur_time = time.gmtime()
    return (cur_time.tm_hour * 3600 + cur_time.tm_min * 60 + cur_time.tm_sec)

def find_max_cams(filename):
    cam_dict = create_cam_dict(filename)
    min_start = -1
    max_end = -1
    for cam_id in cam_dict:
        if (min_start == -1 or max_end == -1):
            min_start = cam_dict[cam_id][0]
            max_end = cam_dict[cam_id][1]
        else:
            start = cam_dict[cam_id][0]
            end = cam_dict[cam_id][1]
            if (start < min_start):
                min_start = start
            if (end > max_end):
                max_end = end

    cur_time = min_start
    max_cams = 0
    while (cur_time <= max_end):
        percent = 100 * (cur_time - min_start) / (max_end - min_start)
        #print("\r {0:0.2f}% complete".format(percent), end="\r")
        cur_cams = 0
        for cam_id in cam_dict:
            start = cam_dict[cam_id][0]
            end = cam_dict[cam_id][1]
            if (cur_time >= start and cur_time <= end):
                cur_cams += 1
        if (cur_cams > max_cams):
            max_cams = cur_cams
        cur_time += 1

    #print(" 100.00% complete")
    return max_cams

def run_eclipse(readfile, writefile, interval):
    cam_list, min_start, max_end = create_cam_list(readfile)
    duration = max_end - min_start
    f = open(writefile, 'w')
    f.write('Camera_ID,is_Video,Duration(secs),Interval,\
    StoreCAM_ID,URL,O/P Filename,Runtime(secs),FPS\n')
    
    for cam in cam_list:
        f.write('{0:d},,{1:d},{2:d},,,,,\n'.format(cam, duration, interval))

    f.close()
    cur_time = get_time()
    if (cur_time > max_end):
        print('Eclipse has already ended. Terminating execution.')
        return
    while (cur_time < min_start - 120): # provide 2 minutes to prep
        sys.stdout.write('\rWaiting for Eclipse to start in {0:d} seconds'\
                         .format(min_start - cur_time))
        sys.stdout.flush()

    print('')
    try:
        archiver.archiver(['archiver.py', '-f', writefile])
    except KeyboardInterrupt:
        print('Keyboard Interrupt detected. Terminating execution.')
    else:
        print('Eclipse is over. Terminating execution')

if __name__ == "__main__":
    run_eclipse("eclipse_cams_new.csv", "test.csv", 1)
