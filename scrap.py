import argparse, json, os, shutil
from uuid import uuid4
from config import Config
from scrappers import scrapper_options, get_scrapper
from multiprocessing import cpu_count

from scrappers.base_scrapper import BaseScrapper, BaseTextScrapper

scrapper_ids = [e.scrapper_id for e in scrapper_options]

parser = argparse.ArgumentParser()

# scrapper_id
parser.add_argument(
    "--scrapper_id",
    help="ID of scrapper to be used",
    choices=scrapper_ids,
    required=True,
    type=str,
)

# base_url
parser.add_argument(
    "--base_url",
    help="Base URL to be scrapped",
    required=True,
    type=str,
)

# max_threads
parser.add_argument(
    "--max_threads",
    help="Number of parallel threads to use for scrapping",
    default=cpu_count(),
    required=False,
    type=int,
)

# output_dir
parser.add_argument(
    "--output_dir",
    help="Output folder for the scrapped data",
    default="./output",
    required=False,
    type=str,
)

# dedup_lines
parser.add_argument(
    "--dedup_lines",
    help="Remove duplicate lines from output",
    default=False,
    required=False,
    type=bool,
)

# recursive
parser.add_argument(
    "--recursive",
    help="Recursively scrap all urls extracted from base_url and then scrap them",
    action="store_true",
)

# max_url_count
parser.add_argument(
    "--max_url_count",
    help="Maximum number of URLs to be scrapped if recursively scrapped",
    default=100,
    required=False,
    type=int,
)

# download_files
parser.add_argument(
    "--download_files",
    help="Downloads additional files like images, PDFs, etc",
    action="store_true",
    default=False,
)

args = parser.parse_args()

config = Config(args)

if os.path.exists(config.output_dir):
    for e in config.output_dir.glob("*"):
        try:
            if os.path.isdir(e):
                shutil.rmtree(config.output_dir)
            else:
                os.remove(e)
        except:
            pass

os.makedirs(config.output_dir, exist_ok=True)

with open("./scrap_settings/scrap_mimes.txt") as f:
    config.scrap_mimes.update(filter(len, f.read().splitlines()))

with open("./scrap_settings/download_mimes.txt") as f:
    config.download_mimes.update(filter(len, f.read().splitlines()))

config_json = json.dumps(
    config.to_dict(),
    indent=4,
    default=str,
)
with open(config.output_dir / "config.json", "w", encoding="utf-8") as f:
    f.write(config_json)

scrapper: BaseScrapper = get_scrapper(config)
scrapper.scrap()

if config.dedup_lines and isinstance(scrapper, BaseTextScrapper):
    os.system(
        f'sort "{scrapper.raw_file_path}" | uniq > "{config.output_dir}/data.dedup.txt"',
    )
