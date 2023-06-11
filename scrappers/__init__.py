from config import Config
from .bs4_scrappers import *
from .selenium_scrappers import *

scrapper_options = [
    GenericBs4TextScrapper,
    GenericBs4DomTreeScrapper,
    GenericSeleniumTextScrapper,
    GenericSeleniumDomTreeScrapper,
]


def get_scrapper(config: Config):
    return {e.scrapper_id: e for e in scrapper_options}[config.scrapper_id](config)
