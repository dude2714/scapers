"""Hacker News scraper using the official Firebase API."""

import requests

BASE_URL = "https://hacker-news.firebaseio.com/v0"


def get_top_stories(limit: int = 10) -> list[dict]:
    """Return the top stories from Hacker News.

    Args:
        limit: Maximum number of stories to return (default 10).

    Returns:
        List of story dicts with keys: id, title, url, score, by, descendants.
    """
    ids_resp = requests.get(f"{BASE_URL}/topstories.json", timeout=10)
    ids_resp.raise_for_status()
    story_ids = ids_resp.json()[:limit]

    stories = []
    for story_id in story_ids:
        item = _get_item(story_id)
        if item and item.get("type") == "story":
            stories.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={item.get('id')}"),
                    "score": item.get("score", 0),
                    "by": item.get("by"),
                    "descendants": item.get("descendants", 0),
                }
            )
    return stories


def get_new_stories(limit: int = 10) -> list[dict]:
    """Return the newest stories from Hacker News.

    Args:
        limit: Maximum number of stories to return (default 10).

    Returns:
        List of story dicts with keys: id, title, url, score, by, descendants.
    """
    ids_resp = requests.get(f"{BASE_URL}/newstories.json", timeout=10)
    ids_resp.raise_for_status()
    story_ids = ids_resp.json()[:limit]

    stories = []
    for story_id in story_ids:
        item = _get_item(story_id)
        if item and item.get("type") == "story":
            stories.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={item.get('id')}"),
                    "score": item.get("score", 0),
                    "by": item.get("by"),
                    "descendants": item.get("descendants", 0),
                }
            )
    return stories


def _get_item(item_id: int) -> dict | None:
    """Fetch a single item by ID from the HN API."""
    resp = requests.get(f"{BASE_URL}/item/{item_id}.json", timeout=10)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("Top 10 Hacker News stories:")
    for i, story in enumerate(get_top_stories(10), 1):
        print(f"{i:2}. [{story['score']}] {story['title']}")
        print(f"     {story['url']}")
