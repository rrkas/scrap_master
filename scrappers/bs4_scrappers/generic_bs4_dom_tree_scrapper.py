import requests
from config import Config
from bs4 import BeautifulSoup
from scrappers.base_scrapper import BaseDomTreeScrapper
from scrappers.bs4_scrappers.utils import recursive_scrap_tree


class GenericBs4DomTreeScrapper(BaseDomTreeScrapper):
    scrapper_id = "generic_bs4_dom_tree"

    def __init__(self, config: Config):
        BaseDomTreeScrapper.__init__(self, config)

    # returns list of all urls on that page
    def scrap_single_url(self, url: str, next_urls: list):
        can_scrap, can_download = self.can_scrap_and_download(url)
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

            self.write_tree_to_file(url, recursive_scrap_tree(soup))

            urls = [self.normalize_url(url, e["href"]) for e in soup.findAll(href=True)]
            urls += [self.normalize_url(url, e["src"]) for e in soup.findAll(src=True)]
            next_urls.extend(urls)

            self.scrapped_urls.add(url)

        if can_download:
            self.download_file(url)
