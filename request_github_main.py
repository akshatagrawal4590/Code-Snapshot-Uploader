import requests
import base64
import os
import urllib3
from datetime import datetime
urllib3.disable_warnings()
from request_jira import main
import utils
def get_all_commits(headers):
    all_commits = []
    page = 1
    print("Processing", end="")
    while True:
        params = {
            "sha": "develop",
            "per_page": 100
        }
        params["page"] = page
        response = requests.get(f"{base_url}/repos/{repo}/commits", headers=headers,params=params,verify=False)
        if response.status_code == 200:
            data = response.json()
            versions = data
            if not versions:
                break
            all_commits.extend(versions)
            print(".", end="")
            page += 1
    return all_commits
def commits_with_jira_story(all_commits,headers,story_number):     
    commits_with_story = []
    response = requests.get(f"{base_url}/repos/{repo}/commits", headers=headers,verify=False)
    if response.status_code == 200:
        commits = response.json()
        print(f"\nCommits with Keyword '{story_number}': \n")
        for commit in all_commits:
            message = commit["commit"]["message"]
            if story_number.lower() in message.lower():
                sha = commit['sha']
                author = commit["commit"]["author"]["name"]
                print(f"- {sha[:7]} by {author}: {message}")
                commits_with_story.append(commit)
        return commits_with_story,response
    else:
        print(f"Status Code: {response.status_code}: {response.text}")
def find_and_create_file(commits_with_story,headers,response):
    if response.status_code == 200:
        print("Connection Established!!")
        found = False
        for commit in commits_with_story:
            sha = commit["sha"]
            commit_url = f"{base_url}/repos/{repo}/commits/{sha}"
            commit_details = requests.get(commit_url, headers=headers, verify=False)
            if commit_details.status_code == 200:
                files = commit_details.json().get("files", [])
                for file in files:
                    filename_only = file["filename"].split("/")[-1]
                    if target_file.lower() in filename_only.lower():
                        full_path = file["filename"]
                        print(f"Found: {full_path} in commit {sha}")
                        content_url = f"{base_url}/repos/{repo}/contents/{full_path}?ref={sha}"
                        content_response = requests.get(content_url, headers=headers, verify=False)
                        if content_response.status_code == 200:
                            content_json = content_response.json()
                            decoded = base64.b64decode(content_json["content"]).decode("utf-8")
                            save_path = os.path.join(os.getcwd(), f"Files/{filename_only}")
                            with open(save_path, "w", encoding="utf-8") as f:
                                f.write(decoded)
                            print(f"\nFile saved as: {save_path}")
                        else:
                            print(f"Found but couldn't fetch the file content: {content_response.status_code}")
                        found = True
            if found:
                break
        if not found:
            print(f"'{target_file}' not found in the commit")
    else:
        print(f"Failed to fetch commits")
if __name__ == "__main__":
    token = utils.github_token
    repo = utils.repo
    base_url = utils.base_url
    result = main()
    commits_flag = False
    for res in result:
        if "No Story" in res["story"]:
            print(f"No Story for the file: {res["file"]}")
        
        target_file = res["file"]
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        if commits_flag == False:
            all_develop_commits = get_all_commits(headers)
            commits_flag = True
        commits_with_story,response = commits_with_jira_story(all_develop_commits,headers,res["story"])
        find_and_create_file(commits_with_story,headers,response)
