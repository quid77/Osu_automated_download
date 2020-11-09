from enum import Enum


#                                           PATHS AND VALUES FOR CHANGE                                           #
#             Only edit right side of the equation of below 5 lines unless you know what you are doing            #
# In the graveyard, there appear approx. 100 beatmaps each day, multiply this by the days you last ran the script #

download_path = "H:\\uTORRENT\\OSU!songs"  # directory for downloads
beatmap_difficulty = 4.5  # difficulty above which beatmapsets containing said beatmap will be downloaded
beatmapsets_to_search = 15000  # number of beatmapsets to examine if they are suitable for download
category = "Graveyard"  # from which category said beatmapsets should be downloaded (Any, Ranked, Graveyard, etc.)
favourites = 3  # number of times beatmapset has been favourited by different players (how liked it is)


class Categories(Enum):  # Also used as "Legend" for above categories
    Any = 1
    Leaderboard = 2
    Ranked = 3
    Qualified = 4
    Loved = 5
    Favourites = 6
    Pending = 7
    Graveyard = 8
    My = 9
