import sys
import re
import archiver
import camera

def test_cams(readfile, writefile, logfile):
    if (readfile is None or writefile is None):
        raise TypeError("\"readfile\" and \"writefile\" may not be Nonetype.")

    try:
        f = open(writefile, 'w')
    except:
        raise ValueError("\"{0:s}\" not writeable.".format(writefile))

    f.close() # closing in case writefile and readfile are the same
    
    try:
        f = open(readfile, 'r')
    except Exception:
        raise ValueError("\"{0:s}\" not readable.".format(readfile))

    header = f.readline()
    if (not re.match(r"id,latitude,longitude,start,end,tot_start,tot_end",\
                     header)):
        raise ValueError("\"readfile\" header doesn't match expected header.")

    # prepare to suppress output from archiver and camera
    real_stdout = sys.stdout
    sys.stdout = open(logfile, 'w')
    
    new_file_str = header
    lines = f.readlines()
    num_lines = len(lines)
    cur_line = 0
    for line in lines:
        real_stdout.write("\r{0:0.2f} % complete".format(cur_line / num_lines))
        real_stdout.flush()
        m = re.search(r"^(\d+),.*,.*,.*,.*,([\d\.:]+),([\d\.:]+)", line)
        if m:
            cam_id = int(m.group(1))
            try:
                cam = archiver.get_camera_db(cam_id, 1, 1)
                cam.get_frame()
            except Exception:
                pass
            else:
                new_file_str += line
    
    sys.stdout.close()
    sys.stdout = real_stdout
    sys.stdout.write('\n')
    f.close()
    f = open(writefile, 'w')
    f.write(new_file_str)
    f.close()
    return

    
if __name__ == '__main__':
    try:
        readfile = sys.argv[1]
        writefile = sys.argv[2]
        logfile = sys.argv[3]
    except IndexError:
        raise Exception("Usage: python2 test_cams.py <readfile> <writefile> \
        <logfile>")
    test_cams(readfile, writefile, logfile)
