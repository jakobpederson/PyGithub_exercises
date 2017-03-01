#!python

from github import Github


class GithubClass:

    def __init__(self, token):
        self.token = token
        self.client = Github(token)

    def get_client(self):
        return self.client

    def get_names_of_repos(self):
        return list(set([x.name for x in self.client.get_user().get_repos()]))

    def create_repo(self, repo_name):
        return self.client.get_user().create_repo(name=repo_name, auto_init=True)

    def get_repos(self):
        return self.client.get_user().get_repos()

    def get_repo(self, repo_name):
        repo_list = list(self.get_repo_gen(repo_name))
        return repo_list[0]

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
            return list(set(list(x.name for x in repo.get_branches())))
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

    def get_branch_files(self, repo, path, branch_name):
        return repo.get_dir_contents(path, branch_name)

    def convert_github_files(self, files):
        data_in_files = []
        for github_file in files:
            data_in_files.extend(github_file.decoded_content.decode("utf-8").split('\n'))
        return data_in_files

    def get_repos_with_branch(self, branch_name):
        repos_with_branch = []
        for repo in self.get_repos():
            try:
                if branch_name in [x.name for x in repo.get_branches()]:
                    repos_with_branch.append(repo.name)
            except:
                pass
        return list(set(repos_with_branch))

    def get_file_names(self, files):
        names_of_files = []
        for file in files:
            names_of_files.append(file.name)
        return names_of_files

    def create_list_of_repo_requirements(self, repo, branch, path, files):
        new_list = []
        for item in self.convert_github_files(files):
            new_list.append([repo.name, branch,  path, item])
        return new_list

    def split_out_versions(self, list_of_lists):
        import re
        for single_list in list_of_lists:
            new_list = re.sub(r'(?<!,)([=<>])', r',\1', single_list[3], count=1)
            single_list.pop(3)
            single_list.extend(new_list.split(","))
        return list_of_lists

    def create_repo_files_dict(self, list_of_repo_names, branch_name):
        repo_files = {}
        for repo_name in list_of_repo_names:
            repo_files[repo_name] = self.get_branch_files(self.get_repo(repo_name), "requirements", branch_name)
        return repo_files


