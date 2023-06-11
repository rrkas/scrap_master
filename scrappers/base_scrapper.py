import os, mimetypes, json, threading, hashlib
import urllib.parse, urllib.request
from config import Config
import requests
from tqdm import tqdm


class BaseScrapper:
    def __init__(self, config: Config):
        self.config = config
        self.visited_urls = dict()  # avoid loops, details of url visited
        self.scrapped_urls = set()
        self.downloads = {}

    def scrap(self):
        urls = self.scrap_urls_batch([self.config.base_url])
        while (
            self.config.recursive
            and len(urls) > 0
            and len(self.scrapped_urls) <= self.config.max_url_count
        ):
            urls = self.scrap_urls_batch(urls)

        self.flush_all()

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

    def scrap_single_url(self, url: str, next_urls: list):
        raise "Un-implemented"

    def can_scrap_and_download(self, url: str):
        # can_scrap, can_download
        if url in self.visited_urls:
            return False, False

        try:
            # response = requests.head(url)
            # mime_type = str(mimetypes.guess_type(url))
            # mime_type = str(response.headers.get("Content-Type"))
            mime_type = urllib.request.urlopen(url).info().get_content_type()

            return (mime_type in self.config.scrap_mimes), (
                mime_type in self.config.download_mimes
            )
        except BaseException as e:
            # print(url, e)
            self.visited_urls[url] = {"error": str(e)}

        return False, False

    def download_file(self, url: str):
        if not self.config.download_files:
            return

        try:
            downloads_dir = self.config.output_dir / "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            response = requests.get(url)
            mime_type = urllib.request.urlopen(url).info().get_content_type()
            filename = f"{_url_hex(url)}{mimetypes.guess_extension(mime_type)}"
            with open(downloads_dir / filename, "wb") as f:
                f.write(response.content)

            self.downloads[url] = {
                "filename": filename,
                "url": url,
                "content_length": len(response.content),
            }

            self.visited_urls[url] = {"downloaded": True, "filename": filename}
        except BaseException as e:
            self.visited_urls[url] = {"downloaded": False, "error": str(e)}

        if len(self.downloads) % 5 == 0:
            self.flush_all()

    def normalize_url(self, page_url: str, url: str):
        if (
            any(
                [
                    url.startswith(e)
                    for e in [
                        ".",
                        "..",
                        "/",
                        "#",
                        "?",
                    ]
                ]
            )
            or "//" not in url
        ):
            return str(urllib.parse.urljoin(page_url, url))

        return url

    def flush_all(self):
        # visited URLs
        if len(self.visited_urls) > 0:
            with open(
                self.config.output_dir / "visited_urls.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    self.visited_urls.copy(),
                    f,
                    indent=4,
                    default=str,
                )

        # downloads info
        if len(self.downloads) > 0:
            with open(
                self.config.output_dir / "downloads_info.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    list(self.downloads.copy().values()),
                    f,
                    indent=4,
                    default=str,
                )


class BaseTextScrapper(BaseScrapper):
    def __init__(self, config: Config):
        BaseScrapper.__init__(self, config)

        self.data_file_count = 0

    def write_text_to_file(self, url: str, data: str):
        data_dir = self.config.output_dir / "url_wise"
        os.makedirs(data_dir, exist_ok=True)

        file_name = f"{_url_hex(url)}.txt"
        filepath = data_dir / file_name

        if os.path.exists(filepath):
            return

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data.strip())

        self.visited_urls[url] = {
            "filename": file_name,
            "file_size": os.stat(filepath).st_size,
        }

        if self.data_file_count % 100 == 0:
            self.flush_all()


class BaseDomTreeScrapper(BaseScrapper):
    def __init__(self, config: Config):
        BaseScrapper.__init__(self, config)

        self.tree_count = 0

    def write_tree_to_file(self, url: str, tree: dict):
        if len(tree) == 0:
            return

        forest_dir = self.config.output_dir / "forest"
        os.makedirs(forest_dir, exist_ok=True)

        filename = f"{_url_hex(url)}.json"

        with open(
            forest_dir / filename,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                tree,
                f,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

        self.visited_urls[url] = {
            "filename": filename,
            "file_size": os.stat(forest_dir / filename).st_size,
        }

        self.tree_count += 1

        if self.tree_count % 10:
            self.flush_all()


def _url_hex(url: str):
    return hashlib.md5(url.encode("utf-8")).hexdigest()
