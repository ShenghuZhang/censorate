import httpx
from typing import Dict, Optional, List
from app.core.config import Settings
from app.core.logger import get_logger
from app.exceptions import GitHubIntegrationError

logger = get_logger(__name__)


class GitHubService:
    """GitHub integration service."""

    def __init__(self, settings: Settings):
        """Initialize GitHub service."""
        self.settings = settings
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"token {settings.GITHUB_ACCESS_TOKEN}"}
        )

    async def get_repository(self, owner: str, repo: str) -> Dict:
        """Get repository information."""
        logger.info(f"Getting repository: {owner}/{repo}")

        try:
            response = await self.client.get(f"https://api.github.com/repos/{owner}/{repo}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get repository: {e}")
        except Exception as e:
            raise GitHubIntegrationError(f"GitHub API error: {e}")

    async def get_commits(self, owner: str, repo: str, sha: str = "HEAD") -> List[Dict]:
        """Get commits from a repository."""
        logger.info(f"Getting commits from: {owner}/{repo}")

        try:
            response = await self.client.get(f"https://api.github.com/repos/{owner}/{repo}/commits")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get commits: {e}")
        except Exception as e:
            raise GitHubIntegrationError(f"GitHub API error: {e}")

    async def create_issue(self, owner: str, repo: str, title: str, body: str) -> Dict:
        """Create a new issue."""
        logger.info(f"Creating issue in: {owner}/{repo}")

        try:
            response = await self.client.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                json={"title": title, "body": body}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to create issue: {e}")
        except Exception as e:
            raise GitHubIntegrationError(f"GitHub API error: {e}")

    async def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get pull requests from a repository."""
        logger.info(f"Getting pull requests from: {owner}/{repo}")

        try:
            response = await self.client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                params={"state": state}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get pull requests: {e}")
        except Exception as e:
            raise GitHubIntegrationError(f"GitHub API error: {e}")
