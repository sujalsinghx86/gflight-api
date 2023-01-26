import os
from selenium import webdriver


def on_server():
    return os.environ.get("PROD").lower() == "true"


class HerokuChromeDriver:
    @staticmethod
    def _generate_chrome_options():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-sha-usage")
        chrome_options.add_argument("--no-sandbox")
        return chrome_options

    def generate_driver(self):
        chrome_options = self._generate_chrome_options()

        if on_server():
            driver = webdriver.Chrome(
                chrome_options=chrome_options
            )
        else:
            driver = webdriver.Chrome()

        return driver
