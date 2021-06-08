import time

import allure


class main_screen(object):
    # Todo: Add try, exception around all methods with TimeOut and ElementNotFound
    def __init__(self, driver, main_url):
        self.main_url = main_url
        self.driver = driver

    @allure.step("main_screen.go_to() | Navigate to CRM")
    def go_to(self):
        self.driver.get(self.main_url)
        time.sleep(10)

        if not "Google" in self.driver.title:
            raise Exception("Unable to load google page!")
        elem = self.driver.find_element_by_name("q")
        elem.send_keys("BrowserStack")
        elem.submit()
        print(self.driver.title)