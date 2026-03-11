"""
GitHub API Client — Tương tác với GitHub REST API.
Thu thập repositories, README, và thông tin chi tiết.
"""
import asyncio
import base64
from datetime import datetime, timedelta
from typing import Optional
import httpx

from config import GITHUB_TOKEN, GITHUB_API_BASE, REQUEST_DELAY


class GitHubClient:
    """Client async cho GitHub API."""

    def __init__(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHubTechTrends/1.0"
        }
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        )
        self._delay = REQUEST_DELAY

    async def close(self):
        await self.client.aclose()

    async def _request(self, url: str, params: dict = None) -> Optional[dict]:
        """Gửi GET request với retry, exponential backoff và rate limit handling."""
        import random
        import time
        max_attempts = 4
        
        for attempt in range(max_attempts):
            try:
                # Add jitter random sleep to mimic human and avoid API bursts
                jitter = random.uniform(0.5, 2.2)
                await asyncio.sleep(self._delay + jitter)
                
                response = await self.client.get(url, params=params)

                # Kiểm tra hard rate limit header
                remaining = int(response.headers.get("X-RateLimit-Remaining", 999))
                if remaining < 5:
                    reset_at = int(response.headers.get("X-RateLimit-Reset", 0))
                    wait_time = max(reset_at - int(time.time()), 2)
                    
                    if wait_time > 300:  # Không chờ quá 5 phút
                        print(f"[GitHub] Rate limit cạn kiệt, chờ quá lâu ({wait_time}s). Bỏ qua request.")
                        return None
                        
                    print(f"[GitHub] Rate limit gần hết, chờ {wait_time}s...")
                    await asyncio.sleep(wait_time + 1) # Cộng thêm 1s buffer

                if response.status_code == 200:
                    return response.json()
                elif response.status_code in (403, 429):
                    # Abuse protection hoặc secondary rate limits
                    retry_after = int(response.headers.get("Retry-After", 0))
                    if retry_after > 0:
                        wait_time = retry_after
                    else:
                        reset_at = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                        wait_time = max(reset_at - int(time.time()), 60)
                        
                    if wait_time > 300:
                         print(f"[GitHub] Bị chặn do Secondary Limit (403/429), chờ {wait_time}s -> Bỏ qua.")
                         return None
                         
                    print(f"[GitHub] Code {response.status_code} (Limit). Chờ {wait_time}s rồi retry...")
                    await asyncio.sleep(wait_time + random.uniform(1, 3))
                elif response.status_code == 404:
                    return None
                elif response.status_code >= 500:
                    # Server errors -> exponential backoff
                    backoff = (2 ** attempt) + random.uniform(0, 1)
                    print(f"[GitHub] Lỗi server {response.status_code}. Thử lại sau {backoff:.1f}s (Lần {attempt+1}/{max_attempts})")
                    await asyncio.sleep(backoff)
                else:
                    print(f"[GitHub] Lỗi {response.status_code}: {response.text[:200]}")
                    return None # Không retry với các lỗi 4xx khác (như 400, 422)

            except httpx.HTTPError as e:
                backoff = (2 ** attempt) + random.uniform(0.5, 2.0)
                print(f"[GitHub] Lỗi HTTP kết nối (lần {attempt+1}/{max_attempts}): {e}. Thử lại sau {backoff:.1f}s")
                await asyncio.sleep(backoff)

        print(f"[GitHub] Gọi API thất bại sau {max_attempts} lần thử: {url}")
        return None

    async def search_repositories(
        self,
        query: str = "stars:>100",
        sort: str = "stars",
        order: str = "desc",
        per_page: int = None,
        page: int = 1,
    ) -> list[dict]:
        """Tìm kiếm repositories qua GitHub Search API."""
        per_page = per_page or 100
        data = await self._request(
            f"{GITHUB_API_BASE}/search/repositories",
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": min(per_page, 100),
                "page": page,
            }
        )
        if not data or "items" not in data:
            return []

        return [self._parse_repo(item) for item in data["items"]]

    async def search_recent_popular(self, days: int = 7, min_stars: int = 50) -> list[dict]:
        """Tìm repos được tạo gần đây với nhiều stars."""
        date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        query = f"created:>{date_from} stars:>{min_stars}"
        return await self.search_repositories(query=query, sort="stars")

    async def search_by_topic(self, topic: str, min_stars: int = 10) -> list[dict]:
        """Tìm repos theo topic cụ thể."""
        query = f"topic:{topic} stars:>{min_stars}"
        return await self.search_repositories(query=query, sort="stars")

    async def get_repo_details(self, owner: str, repo: str) -> Optional[dict]:
        """Lấy thông tin chi tiết của 1 repo."""
        data = await self._request(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")
        if data:
            return self._parse_repo(data)
        return None

    async def get_readme(self, owner: str, repo: str) -> str:
        """Lấy nội dung README của repo."""
        data = await self._request(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme")
        if data and "content" in data:
            try:
                content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                # Giới hạn 5000 ký tự để tránh quá lớn
                return content[:5000]
            except Exception:
                return ""
        return ""

    async def search_and_get_details(
        self,
        query: str = "stars:>500",
        max_repos: int = 30,
        include_readme: bool = True
    ) -> list[dict]:
        """Tìm repos + lấy README cho phân tích AI."""
        repos = await self.search_repositories(query=query, per_page=max_repos)
        if include_readme:
            for repo in repos:
                parts = repo["full_name"].split("/")
                if len(parts) == 2:
                    readme = await self.get_readme(parts[0], parts[1])
                    repo["readme_content"] = readme
        return repos

    def _parse_repo(self, item: dict) -> dict:
        """Chuyển đổi raw API response thành dict chuẩn."""
        created = None
        if item.get("created_at"):
            try:
                created = datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, TypeError):
                pass

        return {
            "github_id": item.get("id"),
            "name": item.get("name", ""),
            "full_name": item.get("full_name", ""),
            "description": item.get("description") or "",
            "url": item.get("html_url", ""),
            "language": item.get("language") or "",
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "open_issues": item.get("open_issues_count", 0),
            "topics": item.get("topics", []),
            "created_at": created,
        }
