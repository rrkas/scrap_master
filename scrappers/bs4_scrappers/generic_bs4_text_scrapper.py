import threading
import requests
from config import Config
from bs4 import BeautifulSoup
from scrappers.base_scrapper import BaseScrapper


class GenericBs4TextScrapper(BaseScrapper):
    scrapper_id = "generic_bs4_text"

    def __init__(self, config: Config):
        BaseScrapper.__init__(self, config)

    # extracts all text from the page
    # returns list of all urls on that page
    def scrap_single_url(self, url: str, next_urls: list):
        can_scrap, can_download = self.can_scrap_url(url)
        if can_scrap:
            try:
                response = requests.get(url)
            except BaseException as e:
                self.visited_urls[url] = {"error": str(e)}
                return

            if response.status_code != 200:
                self.visited_urls[url] = {"status": response.status_code}
                return

            # check if URL is file or html/ text file
            soup = BeautifulSoup(response.text, "html.parser")

            self.write_to_file(soup.get_text(separator="\n", strip=True))

            urls = [self.normalize_url(url, e["href"]) for e in soup.findAll(href=True)]
            urls += [self.normalize_url(url, e["src"]) for e in soup.findAll(src=True)]
            next_urls.extend(urls)

            self.scrapped_urls.add(url)
            self.visited_urls[url] = {
                "status": response.status_code,
                "content": len(response.content),
            }
        if can_download:
            self.download_file(url)
