from bs4 import BeautifulSoup

class ArxivListingParser:

    @staticmethod
    def parse(html: str) -> list[dict]:

        soup = BeautifulSoup(html, 'lxml')

        articles = []

        for dt in soup.select("dl > dt"):
            abstract_link = dt.select_one('a[href^="/abs/"]')
            if not abstract_link:
                continue
            article_id = abstract_link["href"].split("/abs/")[-1]

            dd = dt.find_next_sibling('dd')
            if not dd:
                continue

            title = dd.select_one(".list-title mathjax")
            authors = dd.select_one(".list-authors")

            articles.append({
                "id": article_id,
                "title": title.get_text(" ", strip=True).replace("Title:", "").strip()
                if title else None,
                "authors": [
                    a.get_text(strip=True)
                    for a in authors.select_one("a")
                    ] if authors else [],
                "pdf_url": f"https://arxiv.org/pdf/{article_id}",
                "abs_url": f"https://arxiv.org/abs/{article_id}",
            })

            return articles