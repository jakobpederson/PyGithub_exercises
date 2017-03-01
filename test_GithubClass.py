#!python

import unittest
import nose
import github
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
            cls.g.create_repo(test_repo_name)
            time.sleep(1)
        cls.repo = cls.g.get_repo("repo1")
        time.sleep(10)
        cls.g.create_branch(cls.repo, "branch1")
        new_file = "/requirements/text.txt"
        new_message = "text for test"
        cls.branch_name = "branch1"
        new_content = 'a==1234\nb>2234,<=2235\nc>3234'
        cls.g.create_file(
             cls.repo, path=new_file, message=new_message, content=new_content, branch=cls.branch_name)
        cls.g.create_branch(cls.g.get_repo("repo2"), "branch1")
        newer_content = "d==2234\ne>3234,<=3235\nf>4234"
        cls.g.create_file(
                cls.g.get_repo("repo2"), path=new_file, message=new_message,
                content=newer_content, branch=cls.branch_name)

    @classmethod
    def tearDownClass(cls):
        for repo_name in cls.test_repos:
            if repo_name in cls.g.get_names_of_repos():
                cls.g.delete_repo(repo_name)

    time.sleep(5)

    def test_get_client(self):
        self.assertTrue(isinstance(self.g.get_client(), github.MainClass.Github))

    def test_create_repo(self):
        self.g.create_repo("repo4")
        time.sleep(5)
        self.assertTrue("repo4" in self.g.get_names_of_repos())
        self.g.delete_repo("repo4")

    def test_delete_repo(self):
        self.g.create_repo("repo4")
        time.sleep(5)
        self.g.delete_repo("repo4")

    def test_get_names_of_repos(self):
        self.assertCountEqual(
                ["repo1", "repo2", "repo3"],
                [x for x in self.g.get_names_of_repos() if x in self.test_repos])

    def test_get_names_of_branches(self):
        self.assertTrue("branch1" in self.g.get_names_of_branches(self.repo.name))

    def test_create_branch(self):
        self.g.create_branch(self.repo, "branch2")
        time.sleep(5)
        self.assertTrue("branch2" in self.g.get_names_of_branches("repo1"))

    def test_protect_branch(self):
        self.g.protect_branch(self.repo, "branch1")
        branch = self.g.get_protected_branch(self.repo, "branch1")
        self.assertTrue(branch.protected)

    def test_create_file(self):
        expected = ['a==1234', 'b>2234,<=2235', 'c>3234']
        files = self.g.get_branch_files(self.repo, "requirements", self.branch_name)
        result = self.g.convert_github_files(files)
        self.assertCountEqual(expected, result)

    def test_get_repos_with_branch(self):
        self.assertCountEqual(["repo1", "repo2"], self.g.get_repos_with_branch("branch1"))

    def test_get_file_name(self):
        files = self.g.get_branch_files(self.repo, "requirements", self.branch_name)
        self.assertCountEqual(["text.txt"], self.g.get_file_names(files))

    def test_create_list_of_repo_requirements(self):
        new_list = []
        repos_with_branch = self.g.get_repos_with_branch(self.branch_name)
        files_dict = self.g.create_repo_files_dict(repos_with_branch, self.branch_name)
        for repo_name, file in files_dict.items():
            new_list.extend(
                    self.g.create_list_of_repo_requirements(
                        self.g.get_repo(repo_name), self.branch_name, "requirements", file))
        self.g.split_out_versions(new_list)
        expected = [
                    ['repo2', 'branch1', 'requirements', 'd', '==2234'],
                    ['repo2', 'branch1', 'requirements', 'e', '>3234', '<=3235'],
                    ['repo2', 'branch1', 'requirements', 'f', '>4234'],
                    ['repo1', 'branch1', 'requirements', 'a', '==1234'],
                    ['repo1', 'branch1', 'requirements', 'b', '>2234', '<=2235'],
                    ['repo1', 'branch1', 'requirements', 'c', '>3234']
                   ]
        self.assertCountEqual(expected, new_list)
