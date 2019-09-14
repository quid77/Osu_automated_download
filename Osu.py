import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time
import sys
from enum import Enum
from selenium.webdriver.common.keys import Keys


class Categories(Enum):
    Any = 1
    Leaderboard = 2
    Ranked = 3
    Qualified = 4
    Loved = 5
    Favourites = 6
    Pending = 7
    Graveyard = 8
    My = 9

#                                           PATHS AND VALUES FOR CHANGE                                           #

download_path = "H:\\uTORRENT\\OSU!songs"  # directory for downloads
beatmap_difficulty = 4.5  # difficulty above which beatmapsets containing said beatmap will be downloaded
beatmapsets_to_search = 15000  # number of beatmapsets to examine if they are suitable for download
Category = "Graveyard"  # from which category said beatmapsets should be downloaded (Any, Ranked, Graveyard, etc.)
Favourites = 4  # number of times beatmapset has been favourited by different players (how liked it is)

class TestClass(unittest.TestCase):

    number_of_downloaded_beatmapsets = 0  # for possible later use in tearDownClass
    Category_nr = eval("Categories." + Category + ".value")

    @classmethod
    def setUpClass(cls):   # setUpClass runs once for ALL tests instead of EVERY
        options = webdriver.ChromeOptions()
        preferences = {"download.default_directory": download_path, "download.prompt_for_download": "false",
                       "safebrowsing.enabled": "false", 'profile.default_content_setting_values.automatic_downloads': 1}
        options.add_experimental_option("prefs", preferences)
        cls.driver = webdriver.Chrome(options=options)

    def test_osu_download(self):
        driver = self.driver
        driver.implicitly_wait(5)
        driver.get("https://osu.ppy.sh/home")
        try:
            driver.find_element_by_xpath('//a[contains(@class,"js-user-login--menu")]').click()
        except (TimeoutException, NoSuchElementException):
            print("Couldn't find or load \"Login\" button on the website?")
        driver.find_element_by_xpath("//input[@name='username']").send_keys("tmpname222")
        driver.find_element_by_xpath("//input[@name='password']").send_keys("ffsjustletme")
        driver.find_element_by_xpath("//span[@class='fas fa-fw fa-sign-in-alt']").click()
        try:
            driver.find_element_by_xpath(
                "//img[@class='nav2__locale-current-flag' or @class='nav-button__locale-current-flag'"
                " and @src='/images/flags/GB.png']")
        except NoSuchElementException:
            driver.find_element_by_xpath("//img[@class='nav2__locale-current-flag' or "
                                         "@class='nav-button__locale-current-flag']").click()
            driver.find_element_by_xpath("//span[@class='nav2-locale-item']//img[@src='/images/flags/GB.png']").click()
        try:
            driver.find_element_by_xpath("//a[contains(text(),'modding watchlist') or contains(text(),'obserwowane dyskusje')]")
        except (TimeoutException, NoSuchElementException):
            print("Couldn't ensure successful login, perhaps website language is not set to English or Polish?")
            sys.exit()
        driver.get("https://osu.ppy.sh/beatmapsets?m=3")
        try:
            driver.find_element_by_xpath("//span[contains(text(), 'Categories') or contains(text(), 'Kategorie')]"
                                         "//following::a[%s]" % TestClass.Category_nr).click()
        except (TypeError, TimeoutException, NoSuchElementException):
            # print(e.__doc__)
            driver.find_element_by_xpath("//div[@class='beatmapsets-search-filter'][3]"
                                         "//a[contains(text(),'Any')]").click()
            print("Couldn't locate \"%s\" category, trying alternative method\nContinuing" % Category)

        # Wait until website loads and sorts at least first 16 elements before proceeding with downloads
        # element_number = driver.find_elements_by_xpath("//i[@class='fas fa-lg fa-download']")
        element_number = driver.find_elements_by_xpath("//div[@class='beatmapset-panel__difficulties']")
        WebDriverWait(driver, 3).until(lambda _: len(element_number) >= 16)
        time.sleep(2)

        page_scroll_times = 1
        list_of_beatmapsets = []  # list of beatmapsets which have at least one beatmap with certain difficulty
        for x in range(round(beatmapsets_to_search/2)):
            try:
                beatmap_difficulties = driver.find_elements_by_xpath(
                    "//div[@class='beatmapset-panel__difficulties']//div[@data-stars>'%s']" % beatmap_difficulty)  # all beatmaps with certain difficulty (i.e. more than 4.5 stars)
                for each_element in beatmap_difficulties:
                    ancestor = driver.find_element_by_xpath("//div[@class='beatmapset-panel__difficulties']//div[@data-stars>'%s']//ancestor::div[6]" % beatmap_difficulty)  # backtrack to the whole element, not just single beatmap (from this level i can easily navigate to buttons like "download" or "play")
                    beatmapset_name = ancestor.find_element_by_xpath(
                        ".//*[contains(@class,'u-ellipsis-overflow b')]").text  # using above element as reference, i can navigate towards its name (i.e. name of the song/beatmapset)
                    if beatmapset_name not in list_of_beatmapsets:  # because some songs can have more than one beatmap above 4.5 stars i don't want to include/download them twice
                        if int(ancestor.find_element_by_xpath(
                                ".//*[contains(@title,'Favourites:')]//span[@class='beatmapset-panel__count-number']").text) >= Favourites:
                            list_of_beatmapsets.append(beatmapset_name)
                            download_button = ancestor.find_element_by_xpath(".//i[@class='fas fa-lg fa-download']")
                            try:
                                driver.execute_script("arguments[0].click();", download_button)  # bypass to "click()" element, not applicable in real testing
                            except (TimeoutException, StaleElementReferenceException):
                                print("One of the elements couldn't be downloaded")
                                TestClass.number_of_downloaded_beatmapsets -= 1
                                list_of_beatmapsets.pop()
                            print(list_of_beatmapsets)
                print("page scroll times %s" % page_scroll_times)
                driver.execute_script("window.scrollBy(0,205)", "")  # 205 is the exact height of one pair of elements
                page_scroll_times += 1
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException):  # scrolls to the last element if error/timeout occurs mid-download
                downloads_done()
                driver.refresh()
                driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
                print("Refreshing - page scroll times: %s" % page_scroll_times)
                WebDriverWait(driver, 5).until(lambda _: len(element_number) >= 16)
                for y in range(page_scroll_times):
                    element_number = driver.find_elements_by_xpath("//div[@class='beatmapsets__item']")
                    try:
                        WebDriverWait(each_element, 0.5).until(lambda _: len(element_number) == 32)
                    except TimeoutException:
                        pass
                    finally:
                        driver.execute_script("window.scrollBy(0,205)", "")
        TestClass.number_of_downloaded_beatmapsets += len(list_of_beatmapsets)
        print("Number of downloaded beatmapsets: %s" % TestClass.number_of_downloaded_beatmapsets)

    # Site is only capable of loading approx. 32 items at the same time (16 pairs), each pair is 970x205px (width x height)
    # if more than 16 pairs are loaded the oldest (top) pair in our list unloads to make space for a new one



    @classmethod
    def tearDownClass(cls):
        print("Searching finished, waiting for all downloads to complete...")
        downloads_done()
        cls.driver.close()


# Polling method to check if all downloads are completed before closing the browser
# Checks "download_path" for any files with .crdownload extension, which is extension of files that are currently
# downloading (cr - chrome, different browsers/download managers will use another way of signature for such files)
# maximum default recursiondepth = 1000, this value is adjustable but it's better to change sleep time and get
# the same effect if we are planning to download many GB's of files / have low network bandwidth


def downloads_done():
    for file_name in os.listdir(download_path):
        if file_name.endswith(".crdownload" or ".part"):  # ".crdownload" for Chrome files ".part" for Firefox
            time.sleep(3)
            downloads_done()
            break  # to prevent recursion return from "sleeping" for no longer existing files


if __name__ == "__main__":
    unittest.main()
