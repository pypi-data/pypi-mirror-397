"""Tests for GitHub repository URL parsing."""

import pytest

from src.repo_parser import RepoRef, extract_repos


class TestRepoExtraction:
    """Test suite for GitHub repo URL extraction."""

    def test_extract_https_url(self) -> None:
        """Should extract HTTPS GitHub URLs."""
        text = "Check out https://github.com/acme/my-repo for details."
        repos = extract_repos(text)

        assert len(repos) == 1
        assert repos[0] == RepoRef("acme", "my-repo")

    def test_extract_ssh_url(self) -> None:
        """Should extract SSH GitHub URLs."""
        text = "Clone with git@github.com:acme/my-repo.git"
        repos = extract_repos(text)

        assert len(repos) == 1
        assert repos[0] == RepoRef("acme", "my-repo")

    def test_extract_ssh_url_without_git_extension(self) -> None:
        """Should extract SSH URLs without .git extension."""
        text = "Clone with git@github.com:acme/my-repo"
        repos = extract_repos(text)

        assert len(repos) == 1
        assert repos[0] == RepoRef("acme", "my-repo")

    def test_extract_multiple_urls(
        self,
        sample_issue_description: str,
    ) -> None:
        """Should extract multiple URLs from text."""
        repos = extract_repos(sample_issue_description)

        assert len(repos) == 3
        assert RepoRef("acme", "main-app") in repos
        assert RepoRef("acme", "shared-lib") in repos
        assert RepoRef("acme", "auth-service") in repos

    def test_deduplication(self) -> None:
        """Should deduplicate identical repos."""
        text = """
        https://github.com/acme/repo
        https://github.com/acme/repo
        https://github.com/ACME/REPO
        """
        repos = extract_repos(text)

        # Should only have one entry (case-insensitive dedup)
        assert len(repos) == 1
        assert repos[0].owner == "acme"  # First occurrence preserved
        assert repos[0].repo == "repo"

    def test_preserves_order(self) -> None:
        """Should preserve order of first occurrence."""
        text = """
        https://github.com/first/repo
        https://github.com/second/repo
        https://github.com/third/repo
        """
        repos = extract_repos(text)

        assert len(repos) == 3
        assert repos[0] == RepoRef("first", "repo")
        assert repos[1] == RepoRef("second", "repo")
        assert repos[2] == RepoRef("third", "repo")

    def test_empty_text_returns_empty_list(self) -> None:
        """Should return empty list for empty text."""
        assert extract_repos("") == []
        assert extract_repos(None) == []  # type: ignore[arg-type]

    def test_no_urls_returns_empty_list(self) -> None:
        """Should return empty list when no URLs found."""
        text = "This text has no GitHub URLs in it."
        assert extract_repos(text) == []

    def test_handles_special_characters_in_names(self) -> None:
        """Should handle special characters allowed in GitHub names."""
        text = "https://github.com/my-org_123/repo.name-test"
        repos = extract_repos(text)

        assert len(repos) == 1
        assert repos[0] == RepoRef("my-org_123", "repo.name-test")

    def test_ignores_non_github_urls(self) -> None:
        """Should ignore non-GitHub URLs."""
        text = """
        https://gitlab.com/acme/repo
        https://bitbucket.org/acme/repo
        https://github.com/valid/repo
        """
        repos = extract_repos(text)

        assert len(repos) == 1
        assert repos[0] == RepoRef("valid", "repo")

    def test_http_and_https_both_work(self) -> None:
        """Should extract both HTTP and HTTPS URLs."""
        text = """
        http://github.com/first/repo
        https://github.com/second/repo
        """
        repos = extract_repos(text)

        assert len(repos) == 2

    def test_project_description_extraction(
        self,
        sample_project_description: str,
    ) -> None:
        """Should extract repos from project descriptions."""
        repos = extract_repos(sample_project_description)

        assert len(repos) == 2
        assert RepoRef("acme", "mobile-app") in repos
        assert RepoRef("acme", "design-system") in repos


class TestRepoRef:
    """Test suite for RepoRef dataclass."""

    def test_equality(self) -> None:
        """RepoRefs with same values should be equal."""
        ref1 = RepoRef("owner", "repo")
        ref2 = RepoRef("owner", "repo")

        assert ref1 == ref2

    def test_inequality(self) -> None:
        """RepoRefs with different values should not be equal."""
        ref1 = RepoRef("owner", "repo1")
        ref2 = RepoRef("owner", "repo2")

        assert ref1 != ref2

    def test_hashable(self) -> None:
        """RepoRef should be hashable for use in sets."""
        ref1 = RepoRef("owner", "repo")
        ref2 = RepoRef("owner", "repo")

        # Should be able to use in set
        refs = {ref1, ref2}
        assert len(refs) == 1

    def test_immutable(self) -> None:
        """RepoRef should be immutable (frozen dataclass)."""
        ref = RepoRef("owner", "repo")

        with pytest.raises(AttributeError):
            ref.owner = "new-owner"  # type: ignore[misc]
