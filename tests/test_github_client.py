import pytest
import pytest_asyncio
from collector.github_client import GitHubClient

@pytest_asyncio.fixture
async def github_client():
    client = GitHubClient()
    yield client
    await getattr(client, "close", lambda: None)()

@pytest.mark.asyncio
async def test_search_repositories(httpx_mock, github_client):
    # Mock search API response
    httpx_mock.add_response(
        url="https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=100&page=1",
        json={
            "items": [
                {
                    "full_name": "test/repo1",
                    "description": "A test repo",
                    "html_url": "https://github.com/test/repo1",
                    "stargazers_count": 100,
                    "forks_count": 20,
                    "language": "Python",
                    "topics": [],
                    "updated_at": "2023-01-01T00:00:00Z"
                }
            ]
        }
    )

    repos = await github_client.search_repositories("language:python")
    assert len(repos) == 1
    assert repos[0]["full_name"] == "test/repo1"

@pytest.mark.asyncio
async def test_get_readme(httpx_mock, github_client):
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo1/readme",
        json={"content": "SGVsbG8gV29ybGQ="} # Base64 for "Hello World"
    )
    
    readme = await github_client.get_readme("test/repo1")
    assert readme == "Hello World"
