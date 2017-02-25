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

    def delete_repo(self, repo_name):
        repo = list(x for x in self.get_repos() if x.name == repo_name)
        if len(repo) > 0:
            repo[0].delete()
        else:
            pass
