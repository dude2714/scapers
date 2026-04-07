"""Quotes scraper for quotes.toscrape.com - a site designed for scraping practice."""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


def get_quotes(pages: int = 1) -> list[dict]:
    """Return quotes from quotes.toscrape.com.

    Args:
        pages: Number of pages to scrape (default 1, each page has ~10 quotes).

    Returns:
        List of quote dicts with keys: text, author, tags, author_url.
    """
    quotes = []
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/page/{page}/"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        quote_divs = soup.select("div.quote")

        if not quote_divs:
            break

        for div in quote_divs:
            text_tag = div.select_one("span.text")
            author_tag = div.select_one("small.author")
            author_link = div.select_one("a")
            tag_tags = div.select("a.tag")

            quotes.append(
                {
                    "text": text_tag.get_text(strip=True) if text_tag else "",
                    "author": author_tag.get_text(strip=True) if author_tag else "",
                    "tags": [t.get_text(strip=True) for t in tag_tags],
                    "author_url": BASE_URL + author_link["href"] if author_link else "",
                }
            )
    return quotes


def get_quotes_by_tag(tag: str) -> list[dict]:
    """Return quotes filtered by a specific tag.

    Args:
        tag: Tag to filter by (e.g. "inspirational", "love").

    Returns:
        List of quote dicts with keys: text, author, tags, author_url.
    """
    quotes = []
    page = 1
    while True:
        url = f"{BASE_URL}/tag/{tag}/page/{page}/"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            break
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        quote_divs = soup.select("div.quote")

        if not quote_divs:
            break

        for div in quote_divs:
            text_tag = div.select_one("span.text")
            author_tag = div.select_one("small.author")
            author_link = div.select_one("a")
            tag_tags = div.select("a.tag")

            quotes.append(
                {
                    "text": text_tag.get_text(strip=True) if text_tag else "",
                    "author": author_tag.get_text(strip=True) if author_tag else "",
                    "tags": [t.get_text(strip=True) for t in tag_tags],
                    "author_url": BASE_URL + author_link["href"] if author_link else "",
                }
            )

        next_btn = soup.select_one("li.next a")
        if not next_btn:
            break
        page += 1

    return quotes


if __name__ == "__main__":
    print("Quotes from quotes.toscrape.com:")
    for quote in get_quotes(pages=1):
        print(f"\n  {quote['text']}")
        print(f"  — {quote['author']}  [{', '.join(quote['tags'])}]")
