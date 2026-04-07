"""Reddit scraper using the public JSON API (no auth required)."""

import requests

BASE_URL = "https://www.reddit.com"
HEADERS = {"User-Agent": "scapers/1.0 (https://github.com/dude2714/scapers)"}


def get_posts(subreddit: str, sort: str = "hot", limit: int = 10) -> list[dict]:
    """Return posts from a subreddit.

    Args:
        subreddit: Subreddit name without the r/ prefix (e.g. "python").
        sort: Sorting method - "hot", "new", "top", or "rising" (default "hot").
        limit: Maximum number of posts to return (default 10, max 100).

    Returns:
        List of post dicts with keys: id, title, author, score, url, permalink,
        num_comments, is_self, selftext.
    """
    valid_sorts = {"hot", "new", "top", "rising"}
    if sort not in valid_sorts:
        raise ValueError(f"sort must be one of {valid_sorts}")

    limit = min(limit, 100)
    url = f"{BASE_URL}/r/{subreddit}/{sort}.json"
    resp = requests.get(url, params={"limit": limit}, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    posts = []
    for child in data.get("data", {}).get("children", []):
        post = child["data"]
        posts.append(
            {
                "id": post.get("id"),
                "title": post.get("title"),
                "author": post.get("author"),
                "score": post.get("score", 0),
                "url": post.get("url"),
                "permalink": BASE_URL + post.get("permalink", ""),
                "num_comments": post.get("num_comments", 0),
                "is_self": post.get("is_self", False),
                "selftext": post.get("selftext", ""),
            }
        )
    return posts


def get_subreddit_info(subreddit: str) -> dict:
    """Return basic info about a subreddit.

    Args:
        subreddit: Subreddit name without the r/ prefix.

    Returns:
        Dict with keys: name, title, description, subscribers, active_users.
    """
    url = f"{BASE_URL}/r/{subreddit}/about.json"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    data = resp.json().get("data", {})
    return {
        "name": data.get("display_name"),
        "title": data.get("title"),
        "description": data.get("public_description", ""),
        "subscribers": data.get("subscribers", 0),
        "active_users": data.get("active_user_count", 0),
    }


if __name__ == "__main__":
    sub = "python"
    print(f"Top 10 hot posts from r/{sub}:")
    for i, post in enumerate(get_posts(sub, limit=10), 1):
        print(f"{i:2}. [{post['score']}] {post['title']}")
        print(f"     {post['permalink']}")
