import os
from selenium import webdriver


class Scrapper:
    def __init__(self, param_dict):
        self.origin_city = param_dict["oci"]
        self.origin_country = param_dict["oco"]
        self.destination_city = param_dict["dci"]
        self.destination_country = param_dict["dco"]
        self.destination_date = param_dict["dd"]
        self.data = self.fetch_data()

    def fetch_data(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-sha-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"), chrome_options=chrome_options)

        driver.get("https://www.google.com")
        return driver.page_source
