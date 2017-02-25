#!python

import unittest
import nose
import github
from github import Github
import github_class
import logging
import logging.config
import time
import github_token

logging.disable(logging.CRITICAL)


class TestGithubClassMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = github_class.GithubClass(github_token.token)
        cls.test_repos = ["repo1", "repo2", "repo3"]
        for test_repo_name in cls.test_repos:
            if test_repo_name not in cls.g.get_names_of_repos():
                cls.g.create_repo(test_repo_name)

    @classmethod
    def tearDownClass(cls):
        time.sleep(10)
        for repo in cls.g.get_repos():
            if repo.name in ["repo1", "repo2", "repo3", "repo4"]:
                cls.g.delete_repo(repo.name)

    def test_get_client(self):
        self.assertTrue(isinstance(self.g.get_client(), github.MainClass.Github))

    def test_create_repo(self):
        if "repo4" not in self.g.get_names_of_repos():
            self.g.create_repo("repo4")
        self.assertTrue("repo4" in self.g.get_names_of_repos())

    def test_delete_repo(self):
        if "repo4" not in self.g.get_names_of_repos():
            self.g.create_repo("repo4")
            time.sleep(30)
        self.g.delete_repo("self4")
        self.assertTrue("self4" not in self.g.get_names_of_repos())

    def test_get_names_of_repos(self):
        self.assertCountEqual(
                ["repo1", "repo2", "repo3"],
                list(x for x in self.g.get_names_of_repos() if x in self.test_repos)
                            )

    def test_get_names_of_branches(self):
        self.assertTrue("legacy" in self.g.get_names_of_branches("PyGithub1"))

    def test_create_branch(self):
        self.g.create_branch("repo1", "legacy")
        self.assertTrue("legacy" in self.g.get_names_of_branches("repo1"))
