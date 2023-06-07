import os, uuid, mimetypes, json
import urllib.parse, urllib.request
from config import Config
import requests
from requests import Response


class BaseScrapper:
    def __init__(self, config: Config):
        self.config = config
        self.visited_urls = dict()  # avoid loops, details of url visited
        self.scrapped_urls = set()

        self.raw_file = self.config.output_dir / "data.raw.txt"
        self.temp_file_obj = open(
            self.raw_file,
            "w",
            encoding="utf-8",
        )
        self.line_count = 0

        # additional files (non web-page)
        self.downloads = []

        # mime_types
        self.mime_types = {}

    def scrap(self):
        pass

    def scrap_urls_batch(self, urls: list):
        pass

    def scrap_single_url(self, url: str, next_urls: list):
        pass

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
            print(url, e)

        return False, False

    def download_file(self, url: str):
        if not self.config.download_files:
            return

        try:
            downloads_dir = self.config.output_dir / "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            response = requests.get(url)
            mime_type = urllib.request.urlopen(url).info().get_content_type()
            filename = f"{uuid.uuid4()}.{mimetypes.guess_extension(mime_type)}"
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

    def write_to_file(self, line: str):
        self.temp_file_obj.write(line.strip() + "\n")
        self.line_count += 1
        if self.line_count % 100 == 0:
            self.temp_file_obj.flush()

    def complete(self):
        self.temp_file_obj.flush()
        self.temp_file_obj.close()

        # print(self.mime_types)

        with open(
            self.config.output_dir / "visited_urls.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.visited_urls,
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
