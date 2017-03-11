#!python
import csv
import re
from github import Github


def get_repo_requirements_for_multiprocessing(token, repo):
    branches = ["production", "master"]
    h = GithubClass(token)
    new_list = []
    temp_list = []
    for branch in branches:
        files = h.try_get_branch_files(repo, branch)
        temp_list = h.create_list_of_repo_requirements(repo, branch, "requirements", files)
        h.split_out_versions(temp_list)
        new_list.extend(temp_list)
    return new_list


def write_to_csv_file(list_of_lists):
    with open("output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(list_of_lists)


def get_names_of(list_of_things):
    return list(thing.name for thing in list_of_things)


class GithubClass:

    def __init__(self, token):
        self.token = token
        self.client = Github(token)

    def get_client(self):
        return self.client

    def get_names_of_repos(self):
        repos = self.client.get_user().get_repos()
        return list(set(get_names_of(repos)))

    def create_repo(self, repo_name):
        return self.client.get_user().create_repo(name=repo_name, auto_init=True)

    def get_repos(self):
        return self.client.get_user().get_repos()

    def get_repo(self, repo_name):
        for repo in self.get_repos():
            if repo.name == repo_name:
                return repo

    def delete_repo(self, repo_name):
        self.get_repo(repo_name).delete()

    def get_names_of_branches(self, repo_name):
        if repo_name in self.get_names_of_repos():
            repo = self.get_repo(repo_name)
            branches = repo.get_branches()
            return list(set(get_names_of(branches)))

    def create_branch(self, repo, branch_name):
        sha = repo.get_git_ref('heads/master').object.sha
        return repo.create_git_ref('refs/heads/{}'.format(branch_name), sha)

    def get_branch(self, repo, branch_name):
        for branch in repo.get_branches():
            if branch.name == branch_name:
                return branch

    def protect_branch(self, repo, branch_name):
        repo.protect_branch(branch_name, True, "everyone", ["test"])

    def get_protected_branch(self, repo, branch_name):
        return repo.get_protected_branch(branch_name)

    def create_file(self, repo, path, message, content, branch):
        return repo.create_file(path=path, message=message, content=content, branch=branch)

    def try_get_branch_files(self, repo, branch_name):
        try:
            return self.get_branch_files(repo, "requirements", branch_name)
        except Exception:
            pass

    def get_branch_files(self, repo, path, branch_name):
        return repo.get_dir_contents(path, branch_name)

    def decode_github_files(self, files):
        data_in_files = []
        if files:
            for github_file in files:
                data_in_files.extend(github_file.decoded_content.decode("utf-8").split('\n'))
        return list(value for value in data_in_files if value and value[0] != "-" and value[0] != "#")

    def get_repos_with_branch(self, branch_name):
        repos_with_branch = []
        repos_with_branch.extend(list(self.get_repos_with_branch_gen(branch_name)))
        return repos_with_branch

    def get_repos_with_branch_gen(self, branch_name):
        for repo in self.get_repos():
            branches = repo.get_branches()
            if branch_name in get_names_of(branches):
                yield repo

    def get_file_names(self, files):
        names_of_files = []
        for file in files:
            names_of_files.append(file.name)
        return names_of_files

    def create_list_of_repo_requirements(self, repo, branch, path, files):
        return list([repo.name, branch, item] for item in self.decode_github_files(files))

    def split_out_versions(self, list_of_lists):
        for single_list in list_of_lists:
            new_list = re.sub(r'(?<!,)([=<>])', r',\1', single_list[2], count=1)
            single_list.pop(2)
            single_list.extend(new_list.split(","))
        return list_of_lists
