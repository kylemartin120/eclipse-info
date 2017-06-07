from bs4 import BeautifulSoup
import urllib.request as urllib2
import time

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

if __name__ == "__main__":
    pass
