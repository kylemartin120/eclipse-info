from bs4 import BeautifulSoup
import urllib.request as urllib2
import MySQLdb
import re

"""
The function get_info takes latitude and longitude coordinates and returns a
tuple with the following information, in the following order:

1) total eclipse start time
2) total eclipse end time

If there is no total eclipse for the given location, it will return None.
"""
def get_info(lat, lon):
    # convert lat and lon into degrees, minutes and seconds
    lat_dms = dd_to_dms(lat)
    lon_dms = dd_to_dms(lon)

    # find lat_sign and lon_sign
    if (lat > 0):
        lat_sign = 1
    else:
        lat_sign = -1
    if (lon > 0):
        lon_sign = 1
    else:
        lon_sign = -1
    
    # format the URL
    url = "http://aa.usno.navy.mil/solareclipse?eclipse=22017&place=&lon_sign\
    ={0:d}&lon_deg={1:d}&lon_min={2:d}&lon_sec={3:0.1f}&lat_sign={4:d}&lat_deg\
    ={5:d}&lat_min={6:d}&lat_sec={7:0.1f}&height=0"\
    .format(lon_sign, lon_dms[0], lon_dms[1], lon_dms[2], lat_sign, lat_dms[0],\
            lat_dms[1], lat_dms[2])

    # open the page using BeautifulSoup and urllib2 (try twice)
    num_attempts = 0
    while (num_attempts < 2):
        try:
            num_attempts = 3
            soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
        except:
            num_attempts += 1
    if (num_attempts == 2):
        return None
            
    # find the rows of the table with eclipse information (second table on page)
    try:
        rows = soup.findChildren("table")[1].findChildren("tr")
    except IndexError: # if there is not a second table, there is no eclipse
        return None

    # get eclipse information
    if (len(rows) == 6): # if there are 6 rows, there is a total eclipse
        start = rows[1].findChildren("td")[2].text
        tot_start = rows[2].findChildren("td")[2].text
        tot_end = rows[4].findChildren("td")[2].text
        end = rows[5].findChildren("td")[2].text
        return (start, end, tot_start, tot_end)
    elif (len(rows) == 4): # there is a regular eclipse
        return None
        #start = rows[1].findChildren("td")[2].text
        #end = rows[3].findChildren("td")[2].text
        #return (start, end, None, None)
        
    # no eclipse at this location (although the code should never get here)
    return None

"""
The function dd_to_dms converts a latitude or longitude coordinate from 
decimal degree format into degrees-minutes-seconds format. The function
returns a tuple of degrees, minutes and seconds. Note that the function does
not deal with North-South or East-West, so a negative decimal degree value
will return the same values as its opposite.
"""
def dd_to_dms(dd):
    dd = abs(dd)
    d = int(dd)
    m = int((dd - d) * 60)
    s = (dd - d - (m/60)) * 3600
    return (d, m, s)

"""
The funcion print_progress prints a progress bar and a percentage of the task
completed. It needs to have passed to it the number of iterations completed
as well as the number of total iterations.
"""
def print_progress(complete, total, cams):
    LENGTH = 25 # the total character length of the progress bar
    per = 100 * complete / total
    filled = '#' * int((per / 100) * LENGTH)
    empty = '-' * (LENGTH - int((per / 100) * LENGTH))
    print("\r|{0:s}{1:s}| {2:0.2f}%; {3:d} cams found"\
          .format(filled, empty, per, cams), end="\r")
    if (complete == total):
        print()
    return

"""
The function test_cameras iterates through each item in the "camera" table
within the SQL library "cam2" and determines which ones will capture the
eclipse (based solely on location), and whether it will capture a total
eclipse. For those cameras that do, it will add them to a dictionary, where
the key is the camera id (as provided in the SQL table) and the data is
the tuple returned by the function get_info.
"""

def test_cameras(filename, logname):
    # define latitude and longitude cutoffs (in terms of decimal degrees)
    LAT_H = 45.5
    LAT_L = 32
    LON_H = -78
    LON_L = -125
    
    # open the connection to the SQL database
    connection = MySQLdb.connect("localhost", "root", "", "cam2")
    cursor = connection.cursor()

    # get the id, latitude and longitude of all items in the camera table
    num_rows = cursor.execute("SELECT id, latitude, longitude FROM camera")

    # create an empty dictionary
    eclipse_cams = {}

    # open the files and find the current status of the program
    prev_ids = []
    try:
        f = open(filename, 'r')    
        f_log = open(logname, 'r')
        if (re.match(r"id,latitude,longitude,start,end,tot_start,tot_end",\
                     f.readline())):
            lines = f.readlines()
            num_cams = len(lines)
            for line in lines:
                m = re.match(r"^(\d+),", line)
                if m:
                    prev_ids.append(int(m.group(1))) 
            f.close()
            f = open(filename, 'a')
        else:
            num_cams = 0
            f.close()
            f = open(filename, 'w')
            f.write("id,latitude,longitude,start,end,tot_start,tot_end\n")
        if (re.match(r"id,latitude,longitude\n", f_log.readline())):
            lines = f_log.readlines()
            prev_cnt = len(lines) + num_cams
            for line in lines:
                m = re.match(r"^(\d+),", line)
                if m:
                    prev_ids.append(int(m.group(1)))
            f_log.close
            f_log = open(logname, 'a')
        else:
            f_log.close()
            f_log = open(logname, 'w')
            f_log.write("id,latitude,longitude\n")
    except FileNotFoundError:
        # if no file exists, open the file and write the header
        f = open(filename, 'w')
        f.write("id,latitude,longitude,start,end,tot_start,tot_end\n")
        f_log = open(logname, 'w')
        f_log.write("id,latitude,longitude\n")
        num_cams = 0
        prev_cnt = 0
    
    # iterate through each item row in the cursor
    last_id = max(prev_ids)
    cnt = 0
    try:
        for row in cursor:
            print_progress(cnt, num_rows, num_cams)
            cam_id = row[0]
            lat = row[1]
            lon = row[2]
            if (cam_id < last_id):
                pass
            elif (lat is None or lon is None):
                f_log.write("{0:d},,\n".format(cam_id))
            elif (lat < LAT_L or lat > LAT_H or lon < LON_L or lon > LON_H):
                f_log.write("{0:d},{1:f},{2:f}\n".format(cam_id,lat,lon))
            else:
                info = get_info(lat, lon)
                if (info is not None):
                    num_cams += 1
                    eclipse_cams[row[0]] = info
                    f.write("{0:d},{1:f},{2:f},{3:s},{4:s},{5:s},{6:s}\n"\
                            .format(cam_id, lat, lon, info[0], info[1],\
                                    str(info[2]), str(info[3])))
            cnt += 1
        print_progress(cnt, num_rows, num_cams)
    except KeyboardInterrupt:
        print("\nUser interrupt detected: saving work and stopping execution")
        
    # close the files
    f.close()
    f_log.close()
    
    # return the dictionary
    return eclipse_cams
    
if __name__ == "__main__":
    cams = test_cameras("eclipse_cams.csv", "cams_log.csv")
