from config import Config
from scrappers.base_scrapper import BaseTextScrapper
from scrappers.selenium_scrappers._driver import get_driver, By


class GenericSeleniumTextScrapper(BaseTextScrapper):
    scrapper_id = "generic_selenium_text"

    def __init__(self, config: Config):
        BaseTextScrapper.__init__(self, config)

    def scrap_single_url(self, url: str, next_urls: list):
        if url in self.scrapped_urls:
            return

        can_scrap, can_download = self.can_scrap_and_download(url)

        if can_scrap:
            try:
                driver = get_driver(url)
                self.write_text_to_file(
                    url, driver.find_element(By.XPATH, "/html/body").text.strip()
                )

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

                self.scrapped_urls.add(url)
            except BaseException as e:
                print(url)
                print("\n".join(str(e).splitlines()[:2]))
                self.visited_urls[url] = {"scraped": False, "error": str(e)}

        if can_download:
            self.download_file(url)
