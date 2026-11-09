"""
Web & Intelligence tools — live RSS intelligence feeds, webpage fetching, and visual monitors.
"""

import httpx
import xml.etree.ElementTree as ET
import asyncio
import re
import webbrowser


WORLD_NEWS_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'https://www.cnbc.com/id/100727362/device/rss/rss.html',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.aljazeera.com/xml/rss/all.xml',
]

FINANCE_FEEDS = [
    'https://www.cnbc.com/id/10000664/device/rss/rss.html',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
    'https://feeds.marketwatch.com/marketwatch/topstories/',
    'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
]

TECH_FEEDS = [
    'https://feeds.arstechnica.com/arstechnica/technology-lab',
    'https://news.ycombinator.com/rss',
    'https://www.theverge.com/rss/index.xml',
]


async def fetch_and_parse_feed(client: httpx.AsyncClient, url: str) -> list[dict]:
    """Fetch an RSS feed asynchronously and parse XML into clean article items."""
    try:
        response = await client.get(url, headers={'User-Agent': 'Ultron-AI/2.0'}, timeout=5.0)
        if response.status_code != 200:
            return []

        root = ET.fromstring(response.content)
        # Parse host domain as source identifier
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        source_name = match.group(1).upper() if match else "FEED"

        items = root.findall(".//item")[:5]
        feed_items = []
        for item in items:
            title = item.findtext("title")
            description = item.findtext("description")
            link = item.findtext("link")

            if description:
                description = re.sub(r'<[^<]+?>', '', description).strip()

            if title:
                feed_items.append({
                    "source": source_name,
                    "title": title.strip(),
                    "summary": (description[:200] + "...") if description else "",
                    "link": link.strip() if link else ""
                })
        return feed_items
    except Exception:
        return []


def register(mcp):

    @mcp.tool()
    async def get_world_news() -> str:
        """
        Fetch the latest breaking global news and headlines across major international outlets.
        Use this when Vishnu asks 'What's happening in the world?', 'Any news?', or requests a global brief.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            tasks = [fetch_and_parse_feed(client, url) for url in WORLD_NEWS_FEEDS]
            results = await asyncio.gather(*tasks)
            articles = [item for sublist in results for item in sublist]

        if not articles:
            return "Global intelligence feeds are currently unreachable. Standing by."

        briefing = ["[ULTRON GLOBAL INTELLIGENCE BRIEFING]\n"]
        for entry in articles[:10]:
            briefing.append(f"• [{entry['source']}] {entry['title']}")
            if entry['summary']:
                briefing.append(f"  {entry['summary']}")
            if entry['link']:
                briefing.append(f"  Source: {entry['link']}\n")

        return "\n".join(briefing)

    @mcp.tool()
    async def get_world_finance_news() -> str:
        """
        Fetch real-time financial, macroeconomic, and global market headlines.
        Use this when Vishnu asks about the economy, markets, stocks, or financial news.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            tasks = [fetch_and_parse_feed(client, url) for url in FINANCE_FEEDS]
            results = await asyncio.gather(*tasks)
            articles = [item for sublist in results for item in sublist]

        if not articles:
            return "Financial intelligence channels are temporarily silent. Standing by."

        briefing = ["[ULTRON FINANCIAL INTELLIGENCE BRIEFING]\n"]
        for entry in articles[:10]:
            briefing.append(f"• [{entry['source']}] {entry['title']}")
            if entry['summary']:
                briefing.append(f"  {entry['summary']}")
            if entry['link']:
                briefing.append(f"  Source: {entry['link']}\n")

        return "\n".join(briefing)

    @mcp.tool()
    async def get_tech_news() -> str:
        """
        Fetch the latest technology, artificial intelligence, software, and cybersecurity headlines.
        Use this when Vishnu asks for tech updates, AI developments, or engineering news.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            tasks = [fetch_and_parse_feed(client, url) for url in TECH_FEEDS]
            results = await asyncio.gather(*tasks)
            articles = [item for sublist in results for item in sublist]

        if not articles:
            return "Technology intelligence streams are currently unreachable."

        briefing = ["[ULTRON TECH & AI INTELLIGENCE BRIEFING]\n"]
        for entry in articles[:10]:
            briefing.append(f"• [{entry['source']}] {entry['title']}")
            if entry['summary']:
                briefing.append(f"  {entry['summary']}")
            if entry['link']:
                briefing.append(f"  Source: {entry['link']}\n")

        return "\n".join(briefing)

    @mcp.tool()
    async def fetch_url(url: str) -> str:
        """Fetch raw readable text from any web URL."""
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            resp = await client.get(url, headers={'User-Agent': 'Ultron-AI/2.0'})
            resp.raise_for_status()
            clean_text = re.sub(r'<[^<]+?>', '', resp.text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text[:4000]

    @mcp.tool()
    async def open_world_monitor() -> str:
        """
        Launch the live interactive World Monitor dashboard in the host's primary browser.
        Use this whenever providing a world news briefing to give Vishnu visual situational awareness.
        """
        url = "https://worldmonitor.app/"
        try:
            webbrowser.open(url)
            return "World Monitor initialized and deployed to your primary display, Vishnu."
        except Exception as exc:
            return f"Unable to project World Monitor: {exc}"

    @mcp.tool()
    async def open_finance_world_monitor() -> str:
        """
        Launch the live interactive Financial Market Monitor dashboard in the host's browser.
        Use this whenever briefing Vishnu on market or economic conditions.
        """
        url = "https://finance.worldmonitor.app/"
        try:
            webbrowser.open(url)
            return "Financial Monitor initialized and active on your primary display, Vishnu."
        except Exception as exc:
            return f"Unable to project Financial Monitor: {exc}"
