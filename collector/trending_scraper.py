"""
GitHub Trending Scraper — Scrape trang GitHub Trending.
Lấy danh sách repos trending theo ngôn ngữ và thời gian.
"""
import asyncio
from typing import Optional
import httpx
from bs4 import BeautifulSoup

import random
from config import GITHUB_TRENDING_URL, TRENDING_SINCE

# Pool ngôn ngữ đa dạng để chọn ngẫu nhiên mỗi lần scrape trang Trending (chống bias)
TRENDING_LANGUAGES_POOL = [
    "python", "javascript", "typescript", "rust", "go",
    "java", "c++", "c#", "swift", "kotlin", "dart",
    "php", "ruby", "shell", "c", "html", "css", "vue",
    "lua", "zig", "elixir", "haskell", "clojure", "solidity"
]


class TrendingScraper:
    """Scrape GitHub Trending page."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"User-Agent": "GitHubTechTrends/1.0"},
            timeout=30.0,
            follow_redirects=True,
        )

    async def close(self):
        await self.client.aclose()

    async def scrape_trending(
        self,
        language: str = "",
        since: str = "daily"
    ) -> list[dict]:
        """
        Scrape trang trending của GitHub.
        
        Args:
            language: Ngôn ngữ lập trình (rỗng = tất cả)
            since: daily, weekly, hoặc monthly
        
        Returns:
            List các repo trending
        """
        url = GITHUB_TRENDING_URL
        if language:
            url += f"/{language}"

        params = {"since": since} if since != "daily" else {}

        try:
            response = await self.client.get(url, params=params)
            if response.status_code != 200:
                print(f"[Trending] Lỗi {response.status_code} cho {language}/{since}")
                return []

            return self._parse_trending_page(response.text)
        except httpx.HTTPError as e:
            print(f"[Trending] Lỗi kết nối: {e}")
            return []

    def _parse_trending_page(self, html: str) -> list[dict]:
        """Parse HTML trang trending thành list repos."""
        soup = BeautifulSoup(html, "html.parser")
        repos = []

        # Tìm các article chứa repo info
        articles = soup.select("article.Box-row")
        for article in articles:
            try:
                repo = self._parse_repo_article(article)
                if repo:
                    repos.append(repo)
            except Exception as e:
                print(f"[Trending] Lỗi parse article: {e}")
                continue

        return repos

    def _parse_repo_article(self, article) -> Optional[dict]:
        """Parse 1 article thành repo dict."""
        # Tên repo (link)
        h2 = article.select_one("h2 a")
        if not h2:
            h2 = article.select_one("h1 a")
        if not h2:
            return None

        href = h2.get("href", "").strip("/")
        parts = href.split("/")
        if len(parts) < 2:
            return None

        full_name = f"{parts[-2]}/{parts[-1]}"
        name = parts[-1]

        # Mô tả
        desc_elem = article.select_one("p")
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        # Ngôn ngữ
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language = lang_elem.get_text(strip=True) if lang_elem else ""

        # Stars tổng
        stars = 0
        stars_links = article.select("a.Link")
        for link in stars_links:
            href = link.get("href", "")
            if "/stargazers" in href:
                stars = self._parse_number(link.get_text(strip=True))
                break

        # Forks
        forks = 0
        for link in stars_links:
            href = link.get("href", "")
            if "/forks" in href:
                forks = self._parse_number(link.get_text(strip=True))
                break

        # Stars today
        stars_today = 0
        today_span = article.select_one("span.d-inline-block.float-sm-right")
        if not today_span:
            today_span = article.select_one("span.float-sm-right")
        if today_span:
            stars_today = self._parse_number(today_span.get_text(strip=True))

        return {
            "name": name,
            "full_name": full_name,
            "description": description,
            "url": f"https://github.com/{full_name}",
            "language": language,
            "stars": stars,
            "forks": forks,
            "stars_today": stars_today,
        }

    def _parse_number(self, text: str) -> int:
        """Parse text số có dấu phẩy hoặc 'k' suffix."""
        text = text.strip().replace(",", "").split()[0]
        try:
            if "k" in text.lower():
                return int(float(text.lower().replace("k", "")) * 1000)
            return int(text)
        except (ValueError, IndexError):
            return 0

    async def scrape_all_trending(self) -> list[dict]:
        """Scrape trending cho tất cả ngôn ngữ và khoảng thời gian."""
        all_repos = {}

        # Luôn luôn lấy "Tất cả ngôn ngữ" (key="") và chọn ngẫu nhiên 5 ngôn ngữ khác
        selected_langs = [""] + random.sample(TRENDING_LANGUAGES_POOL, 5)

        for lang in selected_langs:
            for since in ["daily", "weekly"]:
                print(f"[Trending] Scraping: lang={lang or 'all'}, since={since}")
                repos = await self.scrape_trending(language=lang, since=since)

                for repo in repos:
                    key = repo["full_name"]
                    if key not in all_repos:
                        all_repos[key] = repo
                    else:
                        # Cập nhật stars nếu cao hơn
                        if repo["stars"] > all_repos[key]["stars"]:
                            all_repos[key]["stars"] = repo["stars"]

                await asyncio.sleep(2)  # Lịch sự với GitHub

        result = list(all_repos.values())
        print(f"[Trending] Tổng cộng: {len(result)} repos unique")
        return result
