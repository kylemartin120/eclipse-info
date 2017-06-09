import time
import re

def create_cam_dict(filename):
    cam_dict = {}

    f = open(filename, 'r')
    lines = f.readlines()

    num_fails = 0
    for line in lines:
        m = re.search(r"^(\d+),.*,.*,.*,.*,([\d:\.]+),([\d:\.]+)", line)
        if m:
            cam_id = m.group(1)
            start_time = convert_time(m.group(2))
            end_time = convert_time(m.group(3))
            if (start_time is None or end_time is None):
                num_fails += 1
            else:
                cam_dict[cam_id] = [start_time, end_time]
        else:
            num_fails += 1

    return cam_dict

def convert_time(time_str):
    m = re.search(r"^(\d{2}):(\d{2}):(\d{2})", time_str)
    if m:
        hours = int(m.group(1))
        mins = int(m.group(2))
        secs = int(m.group(3))
        return (hours * 3600 + mins * 60 + secs)

    # if not m
    return None

if __name__ == "__main__":
    pass
