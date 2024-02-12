import feedparser
import json


def rss_to_dict(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        item_dict = {}
        item_dict["title"] = entry.title
        item_dict["link"] = entry.link
        item_dict["pubDate"] = entry.published
        item_dict["description"] = entry.summary
        items.append(item_dict)
    return items


url = "https://risingnepaldaily.com/rss"
items = rss_to_dict(url)
print(json.dumps(items, indent=4, ensure_ascii=False))
