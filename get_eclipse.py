from bs4 import BeautifulSoup
import urllib.request as urllib2
import MySQLdb

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
    url = "http://aa.usno.navy.mil/solareclipse?eclipse=22017&place=&lon_sign={0:d}&lon_deg={1:d}&lon_min={2:d}&lon_sec={3:0.1f}&lat_sign={4:d}&lat_deg={5:d}&lat_min={6:d}&lat_sec={7:0.1f}&height=0".format(lon_sign, lon_dms[0], lon_dms[1], lon_dms[2], lat_sign, lat_dms[0], lat_dms[1], lat_dms[2])

    # open the page using BeautifulSoup and urllib2
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
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
        start = rows[1].findChildren("td")[2].text
        end = rows[3].findChildren("td")[2].text
        return (start, end, None, None)
        
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
def print_progress(complete, total, cams, errs):
    LENGTH = 25 # the total character length of the progress bar
    per = 100 * complete / total
    filled = '#' * int((per / 100) * LENGTH)
    empty = '-' * (LENGTH - int((per / 100) * LENGTH))
    print("\r|{0:s}{1:s}| {2:0.2f}%; {3:d} cams found; {4:d} errors detected"\
          .format(filled, empty, per, cams, errs), end="\r")
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

def test_cameras(filename):
    # open the connection to the SQL database
    connection = MySQLdb.connect("localhost", "root", "", "cam2")
    cursor = connection.cursor()

    # get the id, latitude and longitude of all items in the camera table
    num_rows = cursor.execute("SELECT id, latitude, longitude FROM camera")

    # create an empty dictionary
    eclipse_cams = {}

    # open the file, and write the header
    f = open(filename, 'w')
    f.write("id ## start ## end ## tot_start ## tot_end\n")

    # iterate through each item row in the cursor
    cnt = 0
    num_errs = 0
    num_cams = 0
    print_progress(cnt, num_rows, num_cams, num_errs)
    for row in cursor:
        try:
            info = get_info(row[1], row[2])
        except:
            num_errs += 1
            continue
        if (info is not None):
            num_cams += 1
            eclipse_cams[row[0]] = info
            f.write("{0:d} ## {1:s} ## {2:s} ## {3:s} ## {4:s}\n".format\
                    (row[0], info[0], info[1], str(info[2]), str(info[3])))
        cnt += 1
        print_progress(cnt, num_rows, num_cams, num_errs)

    # close the file
    f.close()
    
    # return the dictionary
    return eclipse_cams
    
if __name__ == "__main__":
    cams = test_cameras("eclipse_cams")
