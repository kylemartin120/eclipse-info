from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re

# use the following url: http://aa.usno.navy.mil/data/docs/SolarEclipses.php

"""
The function get_info takes latitude and longitude coordinates and returns a
tuple with the following information, in the following order:

1) total eclipse start time
2) total eclipse end time

If there is no total eclipse for the given location, it will return None.

A selenium webdriver must also be passed to the function
"""
def get_info(lat, lon, driver):
    # convert lat and lon into degrees, minutes and seconds
    lat_dms = dd_to_dms(lat)
    lon_dms = dd_to_dms(lon)
    
    # navigate to the correct URL
    driver.get("http://aa.usno.navy.mil/data/docs/SolarEclipses.php")

    # find the correct elements, and insert the lattitude and longitude info
    
    
    # find and click the "Get data" button

    # on the new page, find the eclipse information and store it into a tuple

    # return the tuple


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
