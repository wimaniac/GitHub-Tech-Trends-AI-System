import pytest
import pytest_asyncio
from collector.trending_scraper import TrendingScraper

@pytest_asyncio.fixture
async def scraper():
    s = TrendingScraper()
    yield s
    await s.close()

@pytest.mark.asyncio
async def test_scrape_trending_page(httpx_mock, scraper):
    # HTML fake của GitHub Trending (cắt gọn)
    fake_html = """
    <div class="Box-row">
      <h2 class="h3 lh-condensed">
        <a href="/trending/repo1">
          <span class="text-normal">trending / </span>repo1
        </a>
      </h2>
      <p class="col-9 color-fg-muted my-1 pr-4">Test Description</p>
      <div class="f6 color-fg-muted mt-2">
        <span itemprop="programmingLanguage">Python</span>
        <a class="Link--muted d-inline-block mr-3" href="/trending/repo1/stargazers">
          <svg aria-label="star"></svg> 1,500
        </a>
        <a class="Link--muted d-inline-block mr-3" href="/trending/repo1/network/members">
          <svg aria-label="fork"></svg> 300
        </a>
      </div>
    </div>
    """
    httpx_mock.add_response(
        url="https://github.com/trending/python",
        text=fake_html
    )

    repos = await scraper.scrape_trending(language="python", since="daily")
    assert len(repos) == 1
    assert repos[0]["full_name"] == "trending/repo1"
    assert repos[0]["stars"] == 1500
    assert repos[0]["forks"] == 300
    assert repos[0]["language"] == "Python"
