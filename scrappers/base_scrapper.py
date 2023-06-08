import os, uuid, mimetypes, json, threading
import urllib.parse, urllib.request
from config import Config
import requests
from tqdm import tqdm


class BaseScrapper:
    def __init__(self, config: Config):
        self.config = config
        self.visited_urls = dict()  # avoid loops, details of url visited
        self.scrapped_urls = set()

        self.raw_file_path = self.config.output_dir / "data.raw.txt"
        self.raw_file_obj = open(
            self.raw_file_path,
            "w",
            encoding="utf-8",
        )
        self.line_count = 0

        # additional files (non web-page)
        self.downloads = []

        # mime_types
        self.mime_types = {}

    def scrap(self):
        urls = self.scrap_urls_batch([self.config.base_url])
        while (
            self.config.recursive
            and len(urls) > 0
            and len(self.scrapped_urls) <= self.config.max_url_count
        ):
            urls = self.scrap_urls_batch(urls)

        self.flush_all()
        self.raw_file_obj.close()

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

    def can_scrap_url(self, url: str):
        # can_scrap, can_download
        if url in self.visited_urls:
            return False, False

        try:
            # response = requests.head(url)
            # mime_type = str(mimetypes.guess_type(url))
            # mime_type = str(response.headers.get("Content-Type"))
            mime_type = urllib.request.urlopen(url).info().get_content_type()
            if mime_type in self.mime_types:
                self.mime_types[mime_type].append(url)
            else:
                self.mime_types[mime_type] = [url]

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
            filename = f"{uuid.uuid4()}{mimetypes.guess_extension(mime_type)}"
            with open(downloads_dir / filename, "wb") as f:
                f.write(response.content)

            self.downloads.append(
                {
                    "filename": filename,
                    "url": url,
                    "content_length": len(response.content),
                }
            )
            self.visited_urls[url] = {"downloaded": True, "filename": filename}
        except BaseException as e:
            self.visited_urls[url] = {"downloaded": False, "error": str(e)}

        if len(self.downloads) % 5 == 0:
            self.flush_all()

    def write_to_file(self, line: str):
        for l in line.splitlines():
            self.raw_file_obj.write(l.strip() + "\n")
            self.line_count += 1
            if self.line_count % 100 == 0:
                self.flush_all()

    def flush_all(self):
        self.raw_file_obj.flush()

        # visited URLs
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
        with open(
            self.config.output_dir / "downloads_info.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.downloads.copy(),
                f,
                indent=4,
                default=str,
            )

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
