from api.heroku_driver import HerokuChromeDriver

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from urllib.parse import quote_plus as url_encode


class FlightSearchURL:
    """
    CONVERTS API REQUEST'S URL PARAMETERS INTO A GOOGLE SEARCHABLE STRING
    """

    BASE_URL = "https://www.google.com/flights/?q="

    def __init__(self, request_params):
        self.origin_city = request_params["oci"].title()
        self.origin_country = request_params["oco"].title()
        self.destination_city = request_params["dci"].title()
        self.destination_country = request_params["dco"].title()
        self.destination_date = request_params["dd"]

    def generate_search_params(self):
        search_params = f"From {self.origin_city} {self.origin_country} " \
                        f"To {self.destination_city} {self.destination_country} " \
                        f"On {self.destination_date} One Way"
        return url_encode(search_params)

    def generate(self):
        search_url = self.BASE_URL + self.generate_search_params()
        return search_url


class TicketWebElements:
    """
    TAKES IN API'S QUERY PARAMETERS,
    SCRAPES GOOGLE FLIGHTS THROUGH SELENIUM
    RETURNS LIST OF SELENIUM WEB ELEMENTS
    """

    TICKET_XPATH = "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li/div/div[2]/div/" \
                   "div[2]"

    def __init__(self, query_params):
        self.query_url = FlightSearchURL(query_params).generate()
        self.driver = HerokuChromeDriver().generate_driver()
        self.driver.get(self.query_url)
        self.tickets = self.fetch()

    def wait_for_page_load(self):
        wait_obj = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.XPATH, self.TICKET_XPATH))
        )
        return wait_obj

    def fetch(self):
        try:
            self.wait_for_page_load()
        finally:
            ticket_list = self.driver.find_elements_by_xpath(self.TICKET_XPATH)
            return ticket_list


# noinspection PyMethodMayBeStatic
class TicketWebElementsProcessor:
    """
    PROCESSES LIST OF SELENIUM WEB ELEMENTS WHICH CONTAIN TICKET HTML
    """

    def __init__(self, ticket_web_elements_list):
        self.ticket_web_elements_list = ticket_web_elements_list
        self.processed_data = []

    def process(self):
        for element in self.ticket_web_elements_list:
            soup = self._generate_bs4_soup_from_web_element(element)
            processed_ticket = self._process_soup(soup)
            self.processed_data.append(processed_ticket)

    def _generate_bs4_soup_from_web_element(self, element):
        soup = BeautifulSoup(
            element.get_attribute("innerHTML"),
            "html.parser"
        )
        return soup

    def _process_soup(self, soup):
        data = FlightDataExtractorFromSoup(soup)
        processed_ticket = {
            "departure_airport": data.departure_airport,
            "departure_time": data.departure_time,
            "arrival_airport": data.arrival_airport,
            "arrival_time": data.arrival_time,
            "total_duration": data.total_duration,
            "price": data.price,
        }
        return processed_ticket


class FlightDataExtractorFromSoup:
    """
    ORDER OF PROPERTIES:
    FROM where and when TO where and when IN how much time FOR how much money
    """

    def __init__(self, soup):
        self.soup = soup
        self.data_string = self.soup.findAll("div", recursive=False)[1].div.span["aria-label"]

    @property
    def departure_airport(self):
        airport = self.data_string.split("Leaves ")[1].split(" at ")[0]
        return airport

    @property
    def departure_time(self):
        departure_string = self.data_string.split(" at ")[1].split(" and ")[0]
        return {
            "time": departure_string.split(" on ")[0],
            "day": departure_string.split(" on ")[1].split(",")[0],
            "date": departure_string.split(", ")[1]
        }

    @property
    def arrival_airport(self):
        airport = self.data_string.split(" and arrives at ")[1].split(" at ")[0]
        return airport

    @property
    def arrival_time(self):
        arrival_string = self.data_string.split(" and arrives at ")[1].split(" at ")[1][:-1]
        return {
            "time": arrival_string.split(" on ")[0],
            "day": arrival_string.split(" on ")[1].split(",")[0],
            "date": arrival_string.split(", ")[1]
        }

    @property
    def total_duration(self):
        total_duration = self.soup.findAll("div", recursive=False)[2].div.contents[0]
        return total_duration

    @property
    def price(self):
        price = self.soup.findAll("div", recursive=False)[5].div.findAll("div", recursive=False)[1].span.contents[0]
        return price


class API:
    def __init__(self, query_params):
        self._tickets = TicketWebElements(query_params).tickets
        self._processor = TicketWebElementsProcessor(self._tickets)
        self._processor.process()
        self.data = self._processor.processed_data

    def get_data(self):
        data = self._processor.processed_data
        return data
