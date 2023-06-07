Scrap Master
============

Ultimate Scrap tool

Available CLI arguments:
========================
[R] base_url        : Base URL to be scrapped
[O] scrapper_id     : ID of scrapper to be used (default: generic_bs4_text)
[O] max_threads     : Number of parallel threads to use for scrapping (default: cpu count)
[O] output_dir      : Output folder for the scrapped data (default: /root/app/output)
[O] dedup_lines     : Remove duplicate lines from output (default: False)
[O] recursive       : Recursively scrap all urls extracted from base_url and then scrap them (default: False)
[O] max_url_count   : Maximum number of URLs to be scrapped if recursively scrapped (default: 100)
[O] download_files  : Downloads additional files like images, PDFs, etc (default: false)

Legends:
[R] - required
[O] - optional


Sample Command:
===============
docker run \
    -it \
    --rm \
    -v /${PWD}/scrap_settings/scrap_mimes.txt:/root/app/scrap_settings/scrap_mimes.txt \
    -v /${PWD}/scrap_settings/download_mimes.txt:/root/app/scrap_settings/download_mimes.txt \
    -v /${PWD}/outputs:/root/app/output \
    rrka79wal/scrap_master:0.0.1 \
    python scrap.py \
    --base_url "http://docs.python.org/3/tutorial/introduction.html" \
    --max_threads 15 \
    --recursive \
    --download_files \
    --max_url_count 1000
