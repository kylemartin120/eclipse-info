from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re

"""
The function get_info takes latitude and longitude coordinates and returns a
tuple with the following information, in the following order:

1) total eclipse start time
2) total eclipse end time

If there is no total eclipse for the given location, it will return None.

A selenium webdriver must also be passed to the function

Note that the URL "http://aa.usno.navy.mil/data/docs/SolarEclipses.php" is used
"""
def get_info(lat, lon, driver):
    # convert lat and lon into degrees, minutes and seconds
    lat_dms = dd_to_dms(lat)
    lon_dms = dd_to_dms(lon)
    
    # navigate to the correct URL
    driver.get("http://aa.usno.navy.mil/data/docs/SolarEclipses.php")

    # find the latitude and longitude text boxes
    latd_el = driver.find_element_by_id("dega")
    latm_el = driver.find_element_by_id("mina")
    lats_el = driver.find_element_by_id("seca")
    lond_el = driver.find_element_by_id("dego")
    lonm_el = driver.find_element_by_id("mino")
    lons_el = driver.find_element_by_id("seco")

    # find the direction radio buttons
    # note: west and north are selected by default, so it is unecessary to
    # find those elements
    south_rad = driver.find_element_by_id("south")
    east_rad = driver.find_element_by_id("east")

    # find the "Get data" button
    # note: there is no way to discern this "Get data" button from an identical
    # one that appears earlier in the html. Therefore, the code gets a list of
    # all the elements of the type "submit" and takes the second one
    data_btn = driver.find_elements_by_xpath("//*[@type='submit']")[1]

    # insert the latitude data
    latd_el.send_keys(str(lat_dms[0]))
    latm_el.send_keys(str(lat_dms[1]))
    lats_el.send_keys(str(lat_dms[2]))
    if (lat < 0):
        south_rad.click()

    # insert the longitude data
    lond_el.send_keys(str(lon_dms[0]))
    lonm_el.send_keys(str(lon_dms[1]))
    lons_el.send_keys(str(lon_dms[2]))
    if (lon > 0):
        east_rad.click()
    
    # click the "Get data" button
    data_btn.click()
    
    # on the new page, find the eclipse information and store it into a tuple
    eclipse = None
    
    # return the tuple
    return eclipse

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
