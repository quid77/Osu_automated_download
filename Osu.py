import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time
import sys
from enum import Enum
from selenium.webdriver.common.keys import Keys


#                                           PATHS AND VALUES FOR CHANGE                                           #
#             Only edit right side of the equation of below 5 lines unless you know what you are doing            #


download_path = "H:\\uTORRENT\\OSU!songs"  # directory for downloads
beatmap_difficulty = 4.5  # difficulty above which beatmapsets containing said beatmap will be downloaded
beatmapsets_to_search = 15000  # number of beatmapsets to examine if they are suitable for download
Category = "Graveyard"  # from which category said beatmapsets should be downloaded (Any, Ranked, Graveyard, etc.)
Favourites = 4  # number of times beatmapset has been favourited by different players (how liked it is)


class Categories(Enum):  # Also used as "Legend" for above categories
    Any = 1
    Leaderboard = 2
    Ranked = 3
    Qualified = 4
    Loved = 5
    Favourites = 6
    Pending = 7
    Graveyard = 8
    My = 9


class TestClass(unittest.TestCase):

    number_of_downloaded_beatmapsets = 0  # for possible later use in tearDownClass
    Category_nr = eval("Categories." + Category + ".value")
    page_scroll_times = 1
    list_of_beatmapsets = []  # list of beatmapsets which have at least one beatmap with certain difficulty

    @classmethod
    def setUpClass(cls):   # setUpClass runs once for ALL tests instead of EVERY
        options = webdriver.ChromeOptions()
        preferences = {"download.default_directory": download_path, "download.prompt_for_download": "false",
                       "safebrowsing.enabled": "false", 'profile.default_content_setting_values.automatic_downloads': 1}
        options.add_experimental_option("prefs", preferences)
        cls.driver = webdriver.Chrome(options=options)

    @classmethod
    def test_osu_download(self):
        driver = self.driver
        driver.implicitly_wait(5)
        driver.get("https://osu.ppy.sh/home")
        try:
            driver.find_element_by_xpath('//a[contains(@class,"js-user-login--menu")]').click()
        except (TimeoutException, NoSuchElementException):
            print("Couldn't find or load \"Login\" button on the website?")
        driver.find_element_by_xpath("//input[@name='username']").send_keys("tmpname222")  # tmpname222 whythisagain77
        driver.find_element_by_xpath("//input[@name='password']").send_keys("ffsjustletme")   # ffsjustletme 1234512345
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
                                         "//a[contains(text(),'%s')]" % Category).click()
            print("Couldn't locate \"%s\" category, trying alternative method\nContinuing" % Category)

        # Wait until website loads at least first 16 elements before proceeding with downloads
        element_number = driver.find_elements_by_xpath("//div[@class='beatmapset-panel__difficulties']")
        WebDriverWait(driver, 3).until(lambda _: len(element_number) >= 16)
        time.sleep(3)
        for x in range(round(beatmapsets_to_search/2)):
            try:
                TestClass.search_for_beatmapsets()
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException):  # scrolls to the last element if error/timeout occurs mid-download
                try:
                    TestClass.search_for_beatmapsets()
                except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
                    TestClass.reload_and_continue()  # if exception keeps reoccuring, we have no choice but to refresh the page
        TestClass.number_of_downloaded_beatmapsets += len(TestClass.list_of_beatmapsets)
        print("Number of downloaded beatmapsets: %s" % TestClass.number_of_downloaded_beatmapsets)

    # Site is only capable of loading approx. 32 items at the same time (16 pairs), each pair is 970x205px (width x height)
    # if more than 16 pairs are loaded the oldest (top) pair in our list unloads to make space for a new one

    @classmethod
    def search_for_beatmapsets(self):
        driver = self.driver
        ancestor = driver.find_elements_by_xpath(
            "//div[@class='beatmapset-panel__difficulties']//div[@data-stars>'%s']//ancestor::div[6]" % beatmap_difficulty)  # backtrack to the whole element, not just single beatmap (from this level i can easily navigate to buttons like "download" or "play")
        for each_element in ancestor:
            beatmapset_name = each_element.find_element_by_xpath(".//*[contains(@class,'u-ellipsis-overflow b')]").text   # using above element as reference, i can navigate towards its name (i.e. name of the song/beatmapset)
            if beatmapset_name not in TestClass.list_of_beatmapsets:  # because some songs can have more than one beatmap above 4.5 stars i don't want to include/download them twice
                how_liked = each_element.find_element_by_xpath(".//*[contains(@title,'Favourites:')]//span[@class='beatmapset-panel__count-number']").text
                if int(how_liked.replace(",", "")) >= Favourites:
                    TestClass.list_of_beatmapsets.append(beatmapset_name)
                    # download_button = each_element.find_element_by_xpath(".//i[@class='fas fa-lg fa-download']")
                    download_button = each_element.find_element_by_xpath(".//a[contains(@href, '/download') and contains(@href,'/beatmapsets/')]").get_attribute('href')
                    try:
                        # ActionChains(driver).key_down(Keys.CONTROL).click(download_button).key_up(Keys.CONTROL).perform()  # runs in foreground + arbitrary scrolling
                        # download_button.send_keys(Keys.CONTROL + Keys.RETURN)  # causes arbitrary page scrolling
                        # driver.execute_script("window.open('%s', 'new_window')" % download_button)  # doesnt switch focus back
                        # driver.switch_to.window(driver.window_handles[0])  # causes to run in foreground...
                        driver.execute_script("window.open('%s', 'name', 'height=400,width=400')" % download_button)  # doesnt switch focus back
                        # driver.execute_script("arguments[0].click();", download_button)  # bypass to "click()" element, not applicable in real testing
                        time.sleep(2)  # sadly, anything below that will trigger "too many requests error 429"
                    except (TimeoutException, StaleElementReferenceException):
                        print("One of the elements couldn't be downloaded")
                        TestClass.number_of_downloaded_beatmapsets -= 1
                        TestClass.list_of_beatmapsets.pop()
                    print(TestClass.list_of_beatmapsets)
        print("page scroll times %s" % TestClass.page_scroll_times)
        driver.execute_script("window.scrollBy(0,205)", "")  # 205 is the exact height of one pair of elements
        TestClass.page_scroll_times += 1

    @classmethod
    def reload_and_continue(self):
        print("reload and continue")
        driver = self.driver
        downloads_done()
        driver.refresh()
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        print("Refreshing - page scroll times: %s" % TestClass.page_scroll_times)
        element_number = driver.find_elements_by_xpath("//div[@class='beatmapsets__item']")
        try:
            WebDriverWait(driver, 5).until(lambda _: len(element_number) >= 16)
        except TimeoutException:
            pass
        for y in range(TestClass.page_scroll_times):
            try:
                WebDriverWait(element_number, 0.2).until(lambda _: len(element_number) >= 26)
            except TimeoutException:
                pass
            finally:
                driver.execute_script("window.scrollBy(0,205)", "")

    @classmethod
    def tearDownClass(cls):
        print("Searching finished, waiting for all downloads to complete...")
        downloads_done()
        print("Number of downloaded beatmapsets: %s" % TestClass.number_of_downloaded_beatmapsets)
        cls.driver.close()


# Polling method to check if all downloads are completed before closing the browser
# Checks "download_path" for any files with .crdownload extension, which is extension of files that are currently
# downloading (cr - chrome, different browsers/download managers will use another way of signature for such files)
# maximum default recursiondepth = 1000, this value is adjustable but it's better to change sleep time and get
# the same effect if we are planning to download many GB's of files / have low network bandwidth


def downloads_done():
    print("downloads_done")
    for file_name in os.listdir(download_path):
        if file_name.endswith(".crdownload" or ".part"):  # ".crdownload" for Chrome files ".part" for Firefox
            time.sleep(3)
            downloads_done()
            break  # to prevent recursion return from "sleeping" for no longer existing files


if __name__ == "__main__":
    unittest.main()
