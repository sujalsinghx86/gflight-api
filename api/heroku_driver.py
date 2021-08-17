import os
from selenium import webdriver


class HerokuChromeDriver:
    # HEROKU ENVIRONMENT VARIABLES
    CHROME_BIN_ENV_VAR = os.environ.get("GOOGLE_CHROME_BIN")
    CHROME_PATH_ENV_VAR = os.environ.get("CHROME_DRIVER_PATH")

    def _generate_chrome_options(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = self.CHROME_BIN_ENV_VAR
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-sha-usage")
        chrome_options.add_argument("--no-sandbox")
        return chrome_options

    def generate_driver(self):
        chrome_options = self._generate_chrome_options()

        driver = webdriver.Chrome(
            executable_path=self.CHROME_PATH_ENV_VAR,
            chrome_options=chrome_options
        )

        return driver
