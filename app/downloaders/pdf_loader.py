import asyncio
from pathlib import Path
import aiohttp
import aiofiles

class PDFDownloader:
    def __init__(self, output_dir=Path("../data/pdfs"), concurrency=2):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        self.semaphore = asyncio.Semaphore(concurrency)

    async def download_pdf(self, session, article):
        article_id = article["id"]
        output_path = self.output_dir / f"{article_id}.pdf"

        if output_path.exists() and output_path.stat().st_size > 0:
            return True

        async with self.semaphore:

            try:
                async with session.get(article["pdf_url"]) as response:
                    response.raise_for_status()

                    if response.headers.get("Content-Type", "").split(";")[0] != "application/pdf":
                        raise ValueError("Response is not a PDF")

                    content = await response.content.read()
                    if not content.startswith(b"%PDF-"):
                        raise ValueError("Invalid PDF")

                    async with aiofiles.open(output_path, mode="wb") as file:
                        await file.write(content)

                print(f"Downloaded: {article_id}")
                return True
            except Exception as e:
                print(f"Failed to download {article_id}: {e}")
                return False