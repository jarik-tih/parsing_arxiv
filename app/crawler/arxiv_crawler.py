import asyncio
import aiohttp

from app.parsers.listing_parser import ArxivListingParser

class ArxivCrawler:

    BASE_URL = "https://arxiv.org/list/{category}/recent"

    def __init__(self, category="cs.AI", batch_size=50):
        self.category = category
        self.batch_size = batch_size
        self.parser = ArxivListingParser()

    async def fetch_page(self, session, skip):
        url = self.BASE_URL.format(category=self.category)
        params = {"skip": skip, "per_page": self.batch_size}

        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.text()

    async def crawl(self):
        headers = {"User-Agent": "Mozilla/5.0"}

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            skip = 0
            while True:
                html = await self.fetch_page(session, skip)

                articles = self.parser.parse(html)
                if not articles:
                    break

                for article in articles:
                    yield article

                print(
                    f"Collected {len(articles)} articles "
                    f"starting at offset {skip}"
                )

                skip += len(articles)

                if len(articles) < self.batch_size:
                    break

                await asyncio.sleep(3)