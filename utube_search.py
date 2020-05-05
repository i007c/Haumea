import requests
from bs4 import BeautifulSoup


def search_on_utube(fild_search: str, max_item: int = 1):
    fild_search = fild_search.replace(" ", "+")
    url = f"https://youtube.com/results?search_query={fild_search}"
    soup = BeautifulSoup(requests.post(url).text, 'html.parser')
    item_section_ol = soup.find("ol", {"class": "item-section"})
    if item_section_ol == None:
        return None
    else:
        li_item = item_section_ol.find_all("li")
        list_items = []
        for item in li_item:
            video_time = item.find("span", {"class": "video-time"})
            if video_time == None:
                pass
            else:
                video_time = video_time.string
                video_a = item.find("a", {"class": "yt-uix-tile-link"})
                video_title = video_a.string
                video_link = "https://youtube.com" + video_a.get("href")
                list_items.append(
                    {"video_time": video_time, "video_title": video_title, "video_link": video_link})
                max_item -= 1
                if max_item == 0:
                    break
        return list_items
