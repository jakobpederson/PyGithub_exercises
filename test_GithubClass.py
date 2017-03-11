#!python

import unittest
import nose
import github
import github_class
import logging
import logging.config
import time
import github_token
from multiprocessing import Pool

logging.disable(logging.CRITICAL)


def the_test_pool(repo):
    branch = "branch1"
    h = github_class.GithubClass(github_token.test_token)
    files = h.try_get_branch_files(repo, branch)
    if files:
        new_list = h.create_list_of_repo_requirements(repo, branch, "requirements", files)
        h.split_out_versions(new_list)
        return(new_list)


class TestGithubClassMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = github_class.GithubClass(token)
        cls.test_repos = ["repo1", "repo2", "repo3"]
        for test_repo_name in cls.test_repos:
            cls.g.create_repo(test_repo_name)
            time.sleep(1)
        cls.repo = cls.g.get_repo("repo1")
        time.sleep(10)
        cls.branch_name = "branch1"
        content = 'a==1234\nb>2234,<=2235\nc>3234\n- def.txt\n\n#'
        alt_content = "d==2234\ne>3234,<=3235\nf>4234"
        repo_to_content_dict = {"repo1": content, "repo2": alt_content}
        for repo_name in repo_to_content_dict.keys():
            cls.g.create_branch(cls.g.get_repo(repo_name), "branch1")
        new_file = "/requirements/text.txt"
        new_message = "text for test"
        for repo_name, new_content in repo_to_content_dict.items():
            target_repo = cls.g.get_repo(repo_name)
            cls.g.create_file(
               target_repo, path=new_file, message=new_message, content=new_content, branch=cls.branch_name)

    @classmethod
    def tearDownClass(cls):
        for repo_name in cls.test_repos:
            if repo_name in cls.g.get_names_of_repos():
                cls.g.delete_repo(repo_name)

    def test_get_client(self):
        self.assertTrue(isinstance(self.g.get_client(), github.MainClass.Github))

    def test_get_names_of_repos(self):
        self.assertCountEqual(
            ["repo1", "repo2", "repo3"],
            list(x for x in self.g.get_names_of_repos() if x in self.test_repos))

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
        files = self.g.try_get_branch_files(self.repo, self.branch_name)
        result = self.g.decode_github_files(files)
        self.assertCountEqual(expected, result)

    def test_get_repos_with_branch(self):
        repos = self.g.get_repos_with_branch("branch1")
        self.assertCountEqual(["repo1", "repo2"], list(x.name for x in repos))

    def test_get_file_name(self):
        files = self.g.try_get_branch_files(self.repo, self.branch_name)
        self.assertCountEqual(["text.txt"], self.g.get_file_names(files))

    def test_get_branch_files(self):
        files = self.g.try_get_branch_files(self.repo, self.branch_name)
        expected = ['a==1234', 'b>2234,<=2235', 'c>3234']
        self.assertCountEqual(expected, self.g.decode_github_files(files))

    def test_create_list_of_repo_requirements(self):
        new_list = []
        repos_with_branch = self.g.get_repos_with_branch(self.branch_name)
        for repo in repos_with_branch:
            files = self.g.try_get_branch_files(repo, self.branch_name)
            temp_list = self.g.create_list_of_repo_requirements(repo, self.branch_name, "requirements", files)
            self.g.split_out_versions(temp_list)
            new_list.extend(temp_list)
        expected = [
            ['repo2', 'branch1', 'd', '==2234'],
            ['repo2', 'branch1', 'e', '>3234', '<=3235'],
            ['repo2', 'branch1', 'f', '>4234'],
            ['repo1', 'branch1', 'a', '==1234'],
            ['repo1', 'branch1', 'b', '>2234', '<=2235'],
            ['repo1', 'branch1', 'c', '>3234']
            ]
        self.assertCountEqual(expected, new_list)

    def test_pool(self):
        p = Pool(1)
        expected = [
            ['repo1', 'branch1', 'a', '==1234'], ['repo1', 'branch1', 'b', '>2234', '<=2235'],
            ['repo1', 'branch1', 'c', '>3234'], ['repo2', 'branch1', 'd', '==2234'],
            ['repo2', 'branch1', 'e', '>3234', '<=3235'], ['repo2', 'branch1', 'f', '>4234']
            ]
        result = []
        repos = self.g.get_repos_with_branch(self.branch_name)
        result = p.map(the_test_pool, repos)
        flattened_result = list(item for sublist in result for item in sublist)
        self.assertCountEqual(expected, flattened_result)
