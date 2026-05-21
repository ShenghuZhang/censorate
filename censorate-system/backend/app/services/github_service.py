import httpx
import base64
from typing import Dict, Optional, List
from app.core.config import Settings
from app.core.logger import get_logger
from app.exceptions import GitHubIntegrationError

logger = get_logger(__name__)


class GitHubService:
    """GitHub integration service for repository management."""

    def __init__(self, settings: Settings):
        """Initialize GitHub service."""
        self.settings = settings
        token = settings.GITHUB_ACCESS_TOKEN
        self.headers = {"Authorization": f"token {token}"}
        self.client = httpx.AsyncClient(headers=self.headers)
        self.sync_client = httpx.Client(headers=self.headers)

    async def get_repository(self, owner: str, repo: str) -> Dict:
        """Get repository information."""
        try:
            response = await self.client.get(f"https://api.github.com/repos/{owner}/{repo}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get repository: {e}")

    async def get_commits(self, owner: str, repo: str, sha: str = "HEAD") -> List[Dict]:
        """Get commits from a repository."""
        try:
            response = await self.client.get(f"https://api.github.com/repos/{owner}/{repo}/commits")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get commits: {e}")

    async def create_issue(self, owner: str, repo: str, title: str, body: str) -> Dict:
        """Create a new issue."""
        try:
            response = await self.client.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                json={"title": title, "body": body}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to create issue: {e}")

    async def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get pull requests from a repository."""
        try:
            response = await self.client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                params={"state": state}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get pull requests: {e}")

    # --- New methods for code generation push ---

    def create_repository(self, name: str, private: bool = False,
                          description: str = "", auto_init: bool = True) -> Dict:
        """Create a new GitHub repository."""
        try:
            response = self.sync_client.post(
                "https://api.github.com/user/repos",
                json={
                    "name": name,
                    "private": private,
                    "description": description,
                    "auto_init": auto_init,
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to create repository: {e.response.status_code} {e.response.text}")

    def create_blob(self, owner: str, repo: str, content: str) -> str:
        """Create a blob and return its SHA."""
        try:
            response = self.sync_client.post(
                f"https://api.github.com/repos/{owner}/{repo}/git/blobs",
                json={"content": content, "encoding": "utf-8"}
            )
            response.raise_for_status()
            return response.json()["sha"]
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to create blob: {e.response.status_code} {e.response.text}")

    def create_tree(self, owner: str, repo: str, tree_items: List[Dict],
                    base_tree: Optional[str] = None) -> Dict:
        """Create a git tree with multiple files."""
        try:
            payload = {"tree": tree_items}
            if base_tree:
                payload["base_tree"] = base_tree
            response = self.sync_client.post(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to create tree: {e.response.status_code} {e.response.text}")

    def create_commit(self, owner: str, repo: str, message: str, tree_sha: str,
                      parent_sha: Optional[str] = None) -> Dict:
        """Create a commit pointing to a tree."""
        try:
            payload = {
                "message": message,
                "tree": tree_sha,
            }
            if parent_sha:
                payload["parents"] = [parent_sha]

            response = self.sync_client.post(
                f"https://api.github.com/repos/{owner}/{repo}/git/commits",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to create commit: {e.response.status_code} {e.response.text}")

    def update_branch(self, owner: str, repo: str, branch: str, commit_sha: str) -> Dict:
        """Update a branch reference to point to a commit."""
        try:
            response = self.sync_client.patch(
                f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
                json={"sha": commit_sha, "force": False}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to update branch: {e.response.status_code} {e.response.text}")

    def create_initial_commit(self, owner: str, repo: str, branch: str = "main") -> Dict:
        """Get the initial commit SHA from auto_init."""
        try:
            response = self.sync_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise GitHubIntegrationError(f"Failed to get initial commit: {e.response.status_code} {e.response.text}")

    def push_files(self, owner: str, repo: str, files: List,
                   branch: str = "main", commit_message: str = "Initial commit") -> Dict:
        """Push multiple files using Git Trees API (single commit)."""
        # Create blobs and tree items
        tree_items = []
        for f in files:
            content = f.content if hasattr(f, 'content') else f.get('content', '')
            blob_sha = self.create_blob(owner, repo, content)
            tree_items.append({
                "path": f.file_path if hasattr(f, 'file_path') else f.get('file_path', ''),
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            })

        # Get base tree from existing branch
        try:
            ref_data = self.create_initial_commit(owner, repo, branch)
            base_tree_sha = self.sync_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/commits/{ref_data['object']['sha']}"
            ).json()["tree"]["sha"]
        except GitHubIntegrationError:
            base_tree_sha = None

        # Create tree
        tree = self.create_tree(owner, repo, tree_items, base_tree_sha)
        tree_sha = tree["sha"]

        # Create commit
        parent_sha = ref_data["object"]["sha"] if base_tree_sha else None
        commit = self.create_commit(owner, repo, commit_message, tree_sha, parent_sha)
        commit_sha = commit["sha"]

        # Update branch
        self.update_branch(owner, repo, branch, commit_sha)

        return {"sha": commit_sha, "url": f"https://github.com/{owner}/{repo}"}
