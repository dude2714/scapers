"""GitHub Trending scraper using HTML parsing."""

import requests
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"


def get_trending(language: str = "", since: str = "daily") -> list[dict]:
    """Return trending repositories from GitHub.

    Args:
        language: Programming language to filter by (e.g. "python"). Empty string for all.
        since: Time range - "daily", "weekly", or "monthly" (default "daily").

    Returns:
        List of repo dicts with keys: name, description, language, stars, forks, url.
    """
    url = TRENDING_URL
    params = {"since": since}
    if language:
        url = f"{TRENDING_URL}/{language.lower()}"

    resp = requests.get(url, params=params, timeout=10, headers={"Accept-Language": "en"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    articles = soup.select("article.Box-row")

    repos = []
    for article in articles:
        name_tag = article.select_one("h2 a")
        if not name_tag:
            continue

        full_name = name_tag.get_text(strip=True).replace(" ", "").replace("\n", "")
        repo_url = "https://github.com" + name_tag["href"]

        desc_tag = article.select_one("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        lang_tag = article.select_one("[itemprop='programmingLanguage']")
        language_name = lang_tag.get_text(strip=True) if lang_tag else ""

        stars_tags = article.select("a.Link--muted")
        stars_raw = stars_tags[0].get_text(strip=True).replace(",", "") if len(stars_tags) > 0 else "0"
        forks_raw = stars_tags[1].get_text(strip=True).replace(",", "") if len(stars_tags) > 1 else "0"

        repos.append(
            {
                "name": full_name,
                "description": description,
                "language": language_name,
                "stars": int(stars_raw) if stars_raw.isdigit() else 0,
                "forks": int(forks_raw) if forks_raw.isdigit() else 0,
                "url": repo_url,
            }
        )
    return repos


if __name__ == "__main__":
    print("GitHub Trending (daily):")
    for i, repo in enumerate(get_trending(), 1):
        print(f"{i:2}. {repo['name']}  ★{repo['stars']}")
        if repo["description"]:
            print(f"     {repo['description'][:80]}")
