### Script is outdated after recent osu! website update, needs to be completely rewritten, leaving this code just so i don't lose it
# Automated download for Osu!mania beatmapsets

### To run script, install requirements, set below conditions in 'Paths' file and run the script using 'python TestRunner.py' command in the console

This script allows for search and download of beatmapsets based on conditions:
- category (eg. "All", "Ranked", etc.)
- difficulty (eg. >= 4.5 stars)
- favourites (eg. beatmapset favourited >= 10 times)
You also need to specify:
- download_path (existing folder to which beatmapsets will be downloaded)
- beatmapsets_to_search (number of beatmapsets to scan (to check if they are eligible for download)) 

Set above options and run the script, only beatmapsets that fulfil every above condition will be downloaded.

Due to nature of the website, faster downloading is not possible as you will get error 429 (too many requests), which once triggered will time out the script for 10min. Number of downloaded beatmapsets is also time-gated, each hour you can download up to 200 beatmapsets. This time-gate seems to be tied to currently logged-on user account.


### TODO:
- <s> parallel test execution with multiple users logged-on to bypass 200downloads/hour limit. </s>
- Refactoring, QoL improvements