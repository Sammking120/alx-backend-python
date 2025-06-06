#!/usr/bin/env python3
"""Unit tests for GithubOrgClient class in client.py."""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient methods and properties."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct payload."""
        mock_get_json.return_value = {"payload": True}
        client = GithubOrgClient(org_name)  # Create client instance
        result = client.org  # Call org property
        self.assertEqual(result, {"payload": True})  # Verify result
        mock_get_json.assert_called_once_with(  # Check get_json call
            f"https: //api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url returns correct URL."""
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {  # Mock org property
                "repos_url": "https://api.github.com/orgs/test/repos"
            }
            client = GithubOrgClient("test")  # Create client instance
            result = client._public_repos_url  # Access _public_repos_url
            self.assertEqual(result,  # Verify result
                             "https://api.github.com/orgs/test/repos")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns correct repo list."""
        mock_get_json.return_value = [  # Mock get_json response
            {"name": "repo1"},
            {"name": "repo2"}
        ]
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "http://mock/repos"
            client = GithubOrgClient("test")  # Create client instance
            result = client.public_repos()  # Call public_repos
            self.assertEqual(result, ["repo1", "repo2"])  # Verify repo names
            mock_get_json.assert_called_once_with(  # Check get_json call
                "http://mock/repos")
            mock_url.assert_called_once()  # Check _public_repos_url access

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license returns correct boolean."""
        result = GithubOrgClient.has_license(repo, license_key)  # Call method
        self.assertEqual(result, expected)  # Verify result

@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Assign parameterized attributes to the class
        cls.org_payload = cls.org_payload
        cls.repos_payload = cls.repos_payload
        cls.expected_repos = cls.expected_repos
        cls.apache2_repos = cls.apache2_repos

        def get_side_effect(url):
            mock = Mock()
            if url == "https://api.github.com/orgs/google/repos":
                mock.json.return_value = cls.repos_payload
            elif url == "https://api.github.com/orgs/google":
                mock.json.return_value = cls.org_payload
            else:
                raise ValueError(f"Unexpected URL: {url}")
            return mock
        cls.get_patcher = patch('client.requests.get', side_effect=get_side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)