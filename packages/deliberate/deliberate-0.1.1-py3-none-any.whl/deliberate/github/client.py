"""GitHub API Client."""

import httpx
from rich.console import Console

console = Console()


class GitHubClient:
    """A client for interacting with the GitHub API."""

    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True)
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def is_collaborator(self, username: str) -> bool:
        """Check if a user is a collaborator on the repo."""
        url = f"{self.base_url}/collaborators/{username}"
        resp = self.client.get(url)
        return resp.status_code == 204

    def create_comment(self, issue_number: int, body: str) -> int:
        """Post a comment to the issue/PR."""
        url = f"{self.base_url}/issues/{issue_number}/comments"
        resp = self.client.post(url, json={"body": body})
        try:
            resp.raise_for_status()
            return resp.json()["id"]
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Failed to create comment:[/red] {e.response.text}")
            return 0

    def get_reactions(self, comment_id: int) -> list[dict]:
        """Get reactions for a comment."""
        url = f"{self.base_url}/issues/comments/{comment_id}/reactions"
        resp = self.client.get(url)
        try:
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            console.print(f"[yellow]Error checking reactions:[/yellow] {e}")
            return []

    def create_pull_request(self, title: str, body: str, head: str, base: str = "main") -> int:
        """Create a new pull request."""
        url = f"{self.base_url}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        resp = self.client.post(url, json=data)
        try:
            resp.raise_for_status()
            return resp.json()["number"]
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Failed to create PR:[/red] {e.response.text}")
            raise
