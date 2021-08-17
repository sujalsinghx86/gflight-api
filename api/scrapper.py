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
        self.origin_city = request_params["oci"]
        self.origin_country = request_params["oco"]
        self.destination_city = request_params["dci"]
        self.destination_country = request_params["dco"]
        self.destination_date = request_params["dd"]

    def generate_search_params(self):
        search_params = f"from {self.origin_city}, {self.origin_country} " \
                        f"to {self.destination_city}, {self.destination_country} " \
                        f"on {self.destination_date} one way"
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

    TICKET_XPATH = "/html/body/c-wiz[2]/div/div[2]/div/c-wiz/div/c-wiz/div[2]/div[2]" \
                   "/div/div[2]/div[4]/div/div[2]/div/div[1]/div/div[1]/div/div[2]"

    def __init__(self, query_params):
        self.query_url = FlightSearchURL(query_params).generate()
        self.driver = HerokuChromeDriver().generate_driver()
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
            self.driver.quit()
            return ticket_list


# noinspection PyMethodMayBeStatic
class TicketWebElementsProcessor:
    """
    PROCESSES LIST OF SELENIUM WEB ELEMENTS WHICH CONTAIN TICKET HTML
    """

    def __init__(self, ticket_web_elements_list):
        self.ticket_web_elements_list = ticket_web_elements_list
        self.processed_data = []
        self.process()

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
            "departure_time": data.get_departure_time(),
            "arrival_time": data.get_arrival_time(),
            "total_duration": data.get_total_duration(),
            "price": data.get_price(),
            "take_off_airport": data.get_takeoff_airport(),
            "landing_airport": data.get_landing_airport(),
            "invalid_query": False
        }
        return processed_ticket


class FlightDataExtractorFromSoup:
    def __init__(self, soup):
        self.soup = soup

    def get_departure_time(self):
        departure_time = self.soup.findAll("div", recursive=False)[1].div.span.find("g-bubble").span.span.contents[0]
        return departure_time

    def get_arrival_time(self):
        arrival_time = self.soup.findAll("div", recursive=False)[1].div.span
        arrival_time = arrival_time.findAll("g-bubble")[1].span.span.contents[0]
        return arrival_time

    def get_total_duration(self):
        total_duration = self.soup.findAll("div", recursive=False)[2].div.contents[0]
        return total_duration

    def get_price(self):
        price = self.soup.findAll("div", recursive=False)[6].div.findAll("div", recursive=False)[1].span.contents[0]
        return price

    def _airport_string(self):
        airport_data = self.soup.findAll("div", recursive=False)[1].div.span.attrs["aria-label"].split(" arrives at ")
        return airport_data

    def get_takeoff_airport(self):
        airport_data = self._airport_string()
        take_off_airport = airport_data[0].replace("Leaves ", "").split(" at ")[0]
        return take_off_airport

    def get_landing_airport(self):
        airport_data = self._airport_string()
        landing_airport = airport_data[1].split(" at ")[0]
        return landing_airport


class API:
    def __init__(self, query_params):
        self._tickets = TicketWebElements(query_params)
        self._processor = TicketWebElementsProcessor(self._tickets)
        self._processor.process()
        self.data = self._processor.processed_data

    def get_data(self):
        data = self._processor.processed_data
        return data

# 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
