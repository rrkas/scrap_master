# Scrappers Wiki

| Scrapper ID | What can it scrap | Scrapper Features | Scrapper specific CLI args |
| - | - | - | - |
| `generic_bs4_text` | <ul><li>Static HTML Webpages<li>Text<li>Download Files</ul> | <ul><li>Fast<li>Less Effective</ul> |<ul><li>`--download_files`<li>`--dedup_lines`</ul> |
| `generic_selenium_text` | <ul><li>Javascript enabled Webpages with dynamic content<li>Text<li>Download Files</ul> | <ul><li>Slow<li>More Effective</ul> | <ul><li>`--download_files`<li>`--dedup_lines`</ul> |
| `generic_bs4_dom_tree` | <ul><li>Static HTML Webpages<li>HTML DOM as JSON<li>Download Files</ul> | <ul><li>Fast<li>Less Effective</ul> |<ul><li>`--download_files`</ul> |
| `generic_selenium_dom_tree` | <ul><li>Javascript enabled Webpages with dynamic content<li>HTML DOM as JSON<li>Download Files</ul> | <ul><li>Very Slow<li>More Effective</ul> |<ul><li>`--download_files`</ul> |
