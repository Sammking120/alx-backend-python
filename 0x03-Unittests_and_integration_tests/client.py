#!/usr/bin/env python3
"""A github org client for fetching organization and repository data.
This module provides a client for interacting with the GitHub API to fetch
organization details and public repositories, with optional filtering by license.
It includes caching for efficiency and utility functions for nested data access.
"""
from typing import (
    List,
    Dict,
    Optional,
)

from utils import (
    get_json,
    access_nested_map,
    memoize,
)


class GithubOrgClient:
    """Client for interacting with GitHub organization API."""

    ORG_URL = "https://api.github.com/orgs/{org}"  # Base URL for org API


    def __init__(self, org_name: str) -> None:
        """Initialize with organization name."""
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """Fetch and cache organization data from GitHub API."""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Get URL for public repositories from org data."""
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> Dict:
        """Fetch and cache repository data from GitHub API."""
        return get_json(self._public_repos_url)

    def public_repos(self, license: Optional[str] = None) -> List[str]:
        """Get list of public repository names, optionally filtered by license."""
        json_payload = self.repos_payload
        public_repos = [
            repo["name"] for repo in json_payload
            if license is None or self.has_license(repo, license)
        ]

        return public_repos

    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """Check if a repository has the specified license key."""
        assert license_key is not None, "license_key cannot be None"
        try:
            has_license = access_nested_map(repo, ("license", "key")) == license_key
        except KeyError:
            return False
        return has_license