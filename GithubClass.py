#!python

from github import Github

class GithubClass:

    def __init__(self, token):
        self.token = token
        self.client = Github(token)

    def get_client(self):
        return self.client

    def get_names_of_repos(self):
        return list(x.name for x in self.client.get_user().get_repos())

    def create_repo(self, repo_name):
        return self.client.get_user().create_repo(name=repo_name, auto_init=True)

    def get_repos(self):
        return self.client.get_user().get_repos()

    def get_repo(self, repo_name):
        repo_list = list(self.get_repo_gen(repo_name))
        if len(repo_list) > 0:
            return repo_list[0]
        else:
            return "error"

    def get_repo_gen(self, repo_name):
        for repo in self.get_repos():
            if repo.name == repo_name:
                yield repo

    def delete_repo(self, repo_name):
        repo = self.get_repo(repo_name)
        repo.delete()

    def get_names_of_branches(self, repo_name):
        if repo_name in self.get_names_of_repos():
            repo = self.get_repo(repo_name)
            return list(x.name for x in repo.get_branches())
        else:
            pass

    def create_branch(self, repo, branch_name):
        sha = repo.get_git_ref('heads/master').object.sha
        branch = repo.create_git_ref('refs/heads/{}'.format(branch_name), sha)
        return branch

    def get_branch(self, repo, branch_name):
        for branch in repo.get_branches():
            if branch.name == branch_name:
                return branch

    def get_protected_branch(self, repo, branch_name):
        return repo.get_protected_branch(branch_name)

    def protect_branch(self, repo, branch_name):
        repo.protect_branch(branch_name, True, "everyone", ["test"])

    def create_file(self, repo, path, message, content, branch):
        return repo.create_file(path=path, message=message, content=content, branch=branch)

    def get_branch_dir_contents(self, repo, path, branch_name):
        return repo.get_dir_contents(path, branch_name)

    def convert_github_files(self, files):
        for github_file in files:
            data_in_files = github_file.decoded_content.decode("utf-8").split('\n')
        return data_in_files
