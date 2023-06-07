from pathlib import Path


class Config:
    def __init__(self, args):
        assert int(args.max_threads) > 0

        self.scrapper_id: str = args.scrapper_id
        self.base_url: str = args.base_url
        self.max_threads: int = args.max_threads
        self.output_dir: Path = Path(args.output_dir).resolve()
        self.dedup_lines: bool = args.dedup_lines
        self.recursive: bool = args.recursive
        self.max_url_count: int = args.max_url_count
        self.download_files: bool = args.download_files
        self.scrap_mimes = set()
        self.download_mimes = set()

    def to_dict(self):
        return {
            "scrapper_id": self.scrapper_id,
            "base_url": self.base_url,
            "max_threads": self.max_threads,
            "output_dir": self.output_dir,
            "dedup_lines": self.dedup_lines,
            "recursive": self.recursive,
            "max_url_count": self.max_url_count,
            "scrap_mimes": list(self.scrap_mimes),
            "download_mimes": list(self.download_mimes),
            "download_files": self.download_files,
        }
