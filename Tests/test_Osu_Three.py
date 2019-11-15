from selenium import webdriver
import unittest
import Actions
import Paths


class OsuAutomationThree(unittest.TestCase):

    downloaded_beatmapsets = []
    page_scroll_times = 1
    list_of_beatmapsets = []  # list of beatmapsets which could be downloaded but might be skipped due to dl limit

    @classmethod
    def setUpClass(self):   # setUpClass runs once for ALL tests
        options = webdriver.ChromeOptions()
        preferences = {"download.default_directory": Paths.download_path, "download.prompt_for_download": "false",
                       "safebrowsing.enabled": "false", 'profile.default_content_setting_values.automatic_downloads': 1}
        options.add_experimental_option("prefs", preferences)
        self.driver = webdriver.Chrome(options=options)

    @classmethod
    def test_google(self):
        driver = self.driver
        driver.implicitly_wait(5)

        Actions.navigate_to_login(self)
        Actions.login_user_three(self)
        Actions.choose_category(self)

        Actions.run_script(self, 3, 3)

    @classmethod
    def tearDownClass(self):
        driver = self.driver
        print("Searching finished, waiting for all downloads to complete...")
        Actions.downloads_done()
        print("Test Three, number of downloaded beatmapsets: %s" % len(OsuAutomationThree.downloaded_beatmapsets))
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.close()
