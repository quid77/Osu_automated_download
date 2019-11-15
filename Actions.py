import os
import sys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import Paths


user_login = ["tmpname222", "whythisagain77", "placeholder221"]
user_password = ["ffsjustletme", "1234512345", "dontlookhere"]

Category_nr = eval("Categories." + Paths.category + ".value")


def navigate_to_login(self):
    driver = self.driver
    driver.implicitly_wait(5)
    driver.get("https://osu.ppy.sh/home")
    try:
        driver.find_element_by_xpath('//a[contains(@class,"js-user-login--menu")]').click()
    except (TimeoutException, NoSuchElementException):
        print("Couldn't find or load \"Login\" button on the website?")

    # usernames: tmpname222 whythisagain77 placeholder221
    # passwords: ffsjustletme 1234512345 dontlookhere


def login_user_one(self):
    self.driver.find_element_by_xpath("//input[@name='username']").send_keys(user_login[0])
    self.driver.find_element_by_xpath("//input[@name='password']").send_keys(user_password[0])
    self.driver.find_element_by_xpath("//span[@class='fas fa-fw fa-sign-in-alt']").click()


def login_user_two(self):
    self.driver.find_element_by_xpath("//input[@name='username']").send_keys(user_login[1])
    self.driver.find_element_by_xpath("//input[@name='password']").send_keys(user_password[1])
    self.driver.find_element_by_xpath("//span[@class='fas fa-fw fa-sign-in-alt']").click()


def login_user_three(self):
    self.driver.find_element_by_xpath("//input[@name='username']").send_keys(user_login[2])
    self.driver.find_element_by_xpath("//input[@name='password']").send_keys(user_password[2])
    self.driver.find_element_by_xpath("//span[@class='fas fa-fw fa-sign-in-alt']").click()


def choose_category(self):
    driver = self.driver
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
                                     "//following::a[%s]" % Category_nr).click()
    except (TypeError, TimeoutException, NoSuchElementException):
        # print(e.__doc__)
        driver.find_element_by_xpath("//div[@class='beatmapsets-search-filter'][3]"
                                     "//a[contains(text(),'%s')]" % Paths.category).click()
        print("Couldn't locate \"%s\" category, trying alternative method\nContinuing" % Paths.category)

    # Wait until website loads at least first 16 elements before proceeding with downloads
    element_number = driver.find_elements_by_xpath("//div[@class='beatmapset-panel__difficulties']")
    WebDriverWait(driver, 3).until(lambda _: len(element_number) >= 16)
    time.sleep(3)


def run_script(self, start_number, modulo_number):
    for x in range(round(Paths.beatmapsets_to_search / 2)):
        try:
            search_for_beatmapsets(self, start_number, modulo_number)
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException):  # scrolls to the last element if error/timeout occurs mid-download
            try:
                time.sleep(2)
                search_for_beatmapsets(self, start_number, modulo_number)
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
                reload_and_continue(self)  # if exception keeps reoccuring, we have no choice but to refresh the page
    print("Number of downloaded beatmapsets: %s" % len(self.list_of_beatmapsets))


# site allows only 200 downloads (per acc) resetting every hour, reloging triggers refresh,
# which causes loss of all "scroll", this is very time wasting when scrolling through 5000+ beatmapsets, as we would
# need to scroll back every relog. Because of that there are three accounts downloading in parallel, start_number
# describes number of first downloaded beatmapset (so 1,2,3 consecutively for the scripts) whereas modulo_number
# describes every which beatmapset should be downloaded (3 for every script, as we download every third beatmapset
# in every chrome instance)

def search_for_beatmapsets(self, start_number, modulo_number):
    driver = self.driver
    ancestor = driver.find_elements_by_xpath(
        "//div[@class='beatmapset-panel__difficulties']//div[@data-stars>'%s']//ancestor::div[6]" % Paths.beatmap_difficulty)  # backtrack to the whole element, not just single beatmap (from this level i can easily navigate to buttons like "download" or "play")
    for each_element in ancestor:
        beatmapset_name = each_element.find_element_by_xpath(".//*[contains(@class,'u-ellipsis-overflow b')]").text   # using above element as reference, i can navigate towards its name (i.e. name of the song/beatmapset)
        if beatmapset_name not in self.list_of_beatmapsets:  # because some packs can have more than one beatmap above 4.5 stars i don't want to include/download them twice
            how_liked = each_element.find_element_by_xpath(".//*[contains(@title,'Favourites:')]//span[@class='beatmapset-panel__count-number']").text
            if int(how_liked.replace(",", "")) >= Paths.favourites:
                self.list_of_beatmapsets.append(beatmapset_name)
                if (len(self.list_of_beatmapsets) - 1) % modulo_number != start_number - 1:
                    continue
                self.downloaded_beatmapsets.append(beatmapset_name)
                download_button = each_element.find_element_by_xpath(".//a[contains(@href, '/download') and contains(@href,'/beatmapsets/')]").get_attribute('href')
                try:
                    driver.execute_script("window.open('%s', 'name', 'height=400,width=400')" % download_button)
                    time.sleep(5)  # sadly, anything below that will trigger "too many requests error 429"
                except (TimeoutException, StaleElementReferenceException):
                    print("One of the elements couldn't be downloaded")
                    self.downloaded_beatmapsets.pop()
                print(len(self.downloaded_beatmapsets), self.downloaded_beatmapsets)
    driver.execute_script("window.scrollBy(0,205)", "")  # 205 is the exact height of one pair of elements
    self.page_scroll_times += 1


def reload_and_continue(self):
    print("reload and continue")
    driver = self.driver
    downloads_done()
    driver.refresh()
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    print("Refreshing - page scroll times: %s" % self.page_scroll_times)
    element_number = driver.find_elements_by_xpath("//div[@class='beatmapsets__item']")
    try:
        WebDriverWait(driver, 5).until(lambda _: len(element_number) >= 16)
    except TimeoutException:
        pass
    for y in range(self.page_scroll_times):
        try:
            WebDriverWait(element_number, 0.4).until(lambda _: len(element_number) >= 26)
        except TimeoutException:
            pass
        finally:
            driver.execute_script("window.scrollBy(0,205)", "")


# Polling method to check if all downloads are completed before closing the browser
# Checks "download_path" for any files with .crdownload extension, which is extension of files that are currently
# downloading (cr - chrome, different browsers/download managers will use another way of signature for such files)
# maximum default recursiondepth = 1000, this value is adjustable but it's better to change sleep time and get
# the same effect if we are planning to download many GB's of files / have low network bandwidth

def downloads_done():
    print("downloads_done")
    for file_name in os.listdir(Paths.download_path):
        if file_name.endswith(".crdownload" or ".part"):  # ".crdownload" for Chrome files ".part" for Firefox
            time.sleep(3)
            downloads_done()
            break  # to prevent recursion return from "sleeping" for no longer existing files
