# scapers

A collection of miscellaneous Python web scrapers.

## Scrapers

| Scraper | Description | Source |
|---|---|---|
| `hacker_news.py` | Top & new stories from Hacker News | [HN Firebase API](https://github.com/HackerNews/API) |
| `github_trending.py` | Trending repositories on GitHub | [github.com/trending](https://github.com/trending) |
| `reddit.py` | Posts and subreddit info via Reddit's public JSON API | [reddit.com](https://www.reddit.com) |
| `quotes.py` | Quotes from quotes.toscrape.com (scraping practice site) | [quotes.toscrape.com](https://quotes.toscrape.com) |
| `weather.py` | Current weather and 3-day forecast via wttr.in | [wttr.in](https://wttr.in) |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Each scraper can be run directly or imported as a module.

### Hacker News

```python
from scrapers.hacker_news import get_top_stories, get_new_stories

stories = get_top_stories(limit=5)
for story in stories:
    print(story["title"], story["url"])
```

```bash
python -m scrapers.hacker_news
```

### GitHub Trending

```python
from scrapers.github_trending import get_trending

repos = get_trending(language="python", since="weekly")
for repo in repos:
    print(repo["name"], repo["stars"])
```

```bash
python -m scrapers.github_trending
```

### Reddit

```python
from scrapers.reddit import get_posts, get_subreddit_info

posts = get_posts("python", sort="hot", limit=10)
for post in posts:
    print(post["title"])
```

```bash
python -m scrapers.reddit
```

### Quotes

```python
from scrapers.quotes import get_quotes, get_quotes_by_tag

quotes = get_quotes(pages=2)
tagged = get_quotes_by_tag("inspirational")
```

```bash
python -m scrapers.quotes
```

### Weather

```python
from scrapers.weather import get_weather

data = get_weather("London")
print(data["current"]["temp_c"], "°C")
```

```bash
python -m scrapers.weather
```

## Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`
- `lxml`
