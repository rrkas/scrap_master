from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from tqdm import tqdm
from selenium.webdriver.chrome.service import Service

# import chromedriver_autoinstaller
# try:
#     chromedriver_autoinstaller.install()
# except BaseException as e:
#     print(e)


def set_chrome_options():
    chrome_options = Options()
    for e in [
        "enable-automation",
        "start-maximized",
        "disable-infobars",
        "--disable-infobars",
        "--headless",
        "--no-sandbox",
        "--force-device-scale-factor=1",
        "--disable-extensions",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ]:
        chrome_options.add_argument(e)

    chrome_prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return chrome_options


def get_driver(url):
    # start = datetime.datetime.now()
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=set_chrome_options())
    # driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
    driver.implicitly_wait(0.05)
    driver.set_page_load_timeout(60 * 60 * 60)
    driver.get(url)
    # end = datetime.datetime.now()
    # print(end - start)
    return driver
