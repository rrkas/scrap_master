import threading
import requests
from config import Config
from tqdm import tqdm
from bs4 import BeautifulSoup
from scrappers.base_scrapper import BaseScrapper


class GenericBs4TextScrapper(BaseScrapper):
    scrapper_id = "generic_bs4_text"

    def __init__(self, config: Config):
        BaseScrapper.__init__(self, config)

    # use backtracking to visit every page
    def scrap(self):
        urls = self.scrap_urls_batch([self.config.base_url])
        while (
            self.config.recursive
            and len(urls) > 0
            and len(self.scrapped_urls) <= self.config.max_url_count
        ):
            urls = self.scrap_urls_batch(urls)

        self.raw_file_obj.close()

    # recursively called for branching
    def scrap_urls_batch(self, urls: list):
        next_urls = []
        page_threads = []

        for url in tqdm(urls):
            if len(self.scrapped_urls) >= self.config.max_url_count:
                break

            if url in self.visited_urls:
                continue

            t = threading.Thread(
                target=self.scrap_single_url,
                args=(url, next_urls),
            )
            t.start()
            if (
                len(self.scrapped_urls)
                >= self.config.max_url_count - self.config.max_threads
            ):
                t.join()
            page_threads.append(t)

            while sum([t.is_alive() for t in page_threads]) >= self.config.max_threads:
                if len(page_threads) > self.config.max_threads:
                    page_threads = list(filter(lambda t: t.is_alive(), page_threads))

                if (
                    len(self.scrapped_urls)
                    >= self.config.max_url_count - self.config.max_threads
                ):
                    for t in page_threads:
                        t.join()

        while any([t.is_alive() for t in page_threads]):
            pass

        return next_urls

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
            next_urls.extend(urls)
            self.scrapped_urls.add(url)
            self.visited_urls[url] = {
                "status": response.status_code,
                "content": len(response.content),
            }
        if can_download:
            self.download_file(url)
