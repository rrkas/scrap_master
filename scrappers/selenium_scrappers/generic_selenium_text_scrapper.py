import threading
import requests
from config import Config
from tqdm import tqdm
from bs4 import BeautifulSoup
from scrappers.base_scrapper import BaseScrapper
from scrappers.selenium_scrappers._driver import get_driver, By


class GenericSeleniumTextScrapper(BaseScrapper):
    scrapper_id = "generic_selenium_text"

    def __init__(self, config: Config):
        BaseScrapper.__init__(self, config)

    def scrap_single_url(self, url: str, next_urls: list):
        if url in self.scrapped_urls:
            return

        can_scrap, can_download = self.can_scrap_url(url)

        if can_scrap:
            try:
                driver = get_driver(url)
                self.write_to_file(driver.find_element(By.XPATH, "//html").text.strip())

                urls = [
                    self.normalize_url(url, e.get_attribute("href"))
                    for e in driver.find_elements(
                        By.XPATH,
                        "//*[@href]",
                    )
                ]
                urls += [
                    self.normalize_url(url, e.get_attribute("src"))
                    for e in driver.find_elements(
                        By.XPATH,
                        "//*[@src]",
                    )
                ]
                next_urls.extend(urls)

                self.visited_urls[url] = {"scraped": True}
                self.scrapped_urls.add(url)
            except BaseException as e:
                print(e)
                self.visited_urls[url] = {"scraped": False, "error": str(e)}

        if can_download:
            self.download_file(url)
