import base64
import json
from github import Github
from pprint import pprint
from operator import itemgetter

username= "choiceCoin"

ACCESS_TOKEN= "GITHUB_ACCESS_TOKEN"

g= Github(ACCESS_TOKEN)

user= g.get_user(username)

class Github_api():
    def __init__(self, repo):
        self.repo= repo

    def pull_requests(self):
        repo= self.repo
        count_of_pr= 0
        pr_dict= {"pr_name": [], "pr_count":[]}
        pulls = repo.get_pulls(state= "open", sort= "created")
        for i in pulls:
            count_of_pr += 1
            pr_dict["pr_name"].append(i)
        pr_dict["pr_count"].append(count_of_pr)
        return pr_dict

    def issues(self):
        repo= self.repo
        issues_dict= {}
        count_of_issues= 0
        issues= repo.get_issues(state= "open")
        issues_dict["issues_names"]= issues.get_page(0)
        for i in issues:
            count_of_issues +=1 
        issues_dict["issues_counts"]= count_of_issues
        return issues_dict

    def commits(self):
        repo= self.repo
        count_of_commit= 0
        commit = repo.get_commits()
        for i in commit:
            count_of_commit += 1
        return count_of_commit


    def contributors_count(self):
        repo= self.repo
        count_of_contributors= 0
        contributors = repo.get_contributors()
        for i in contributors:
            count_of_contributors += 1
        return count_of_contributors


    def analyze_traffic(self):
        repo= self.repo
        watch_dict= {}
        clones = repo.get_clones_traffic(per="day")
        views = repo.get_views_traffic(per="day")
        best_day = max(*list((day.count, day.timestamp) for day in views["views"]), key=itemgetter(0))
        watch_dict.update({"views": views, "clones_count": clones["count"], "unique_clones": clones["uniques"],
            "views_count": views["count"], "unique_views": views["uniques"]})
        return watch_dict

    def print_repo(self):
        repo= self.repo
        try:
            data= {}
            data['Repo_name']= repo.full_name
            data["Repo_desc"]= repo.description
            data["Date_created"]= repo.created_at
            data["Last_push_date"]= repo.pushed_at
            data["Language"]= repo.language
            data["Number_of_forks"]= repo.forks
            data["Number_of_stars"] = repo.stargazers_count
            data['watchers'] = repo.watchers_count
            data['Number_of_contributors']= Github_api(repo).contributors_count()
            data["Number_of_commits"]= Github_api(repo).commits()
            data["Issues"]= Github_api(repo).issues()
            data["Pull_Requests"]= Github_api(repo).pull_requests()

            print(data)

        except AttributeError as error:
            print ("Error:", error)

for repo in user.get_repos():
    create_engine= Github_api(repo)
    create_engine.print_repo()
    print("="*100)




