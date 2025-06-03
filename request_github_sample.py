import requests
import base64
import os
import urllib3
from datetime import datetime
urllib3.disable_warnings()
# from request_jira import main
import utils
    
token = utils.github_token
repo = utils.repo
base_url = utils.base_url
story_number = "BKSX-1082"
target_file = "pdr_Agg_WBR_Common_Commercial_WAE"
# target_file = "l_ccar_mapping.hql"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
all_commits = []
page = 1
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
        print(page)
        page += 1
print(len(all_commits))
commits_with_story = []
response = requests.get(f"{base_url}/repos/{repo}/commits?sha=develop", headers=headers,verify=False)
if response.status_code == 200:
    commits = response.json()
    # print(commits)
    print(f"\nCommits with Keyword '{story_number}': \n")
    for commit in all_commits:
        message = commit["commit"]["message"]
        if story_number.lower() in message.lower():
            sha = commit['sha']
            author = commit["commit"]["author"]["name"]
            print(f"- {sha[:7]} by {author}: {message}")
            # print(commit)
            commits_with_story.append(commit)
else:
    print(f"Status Code: {response.status_code}: {response.text}")
# print(commits_with_story)
if response.status_code == 200:
    commits = response.json()
    found = False
    for commit in commits_with_story:
        print("-----------------------------------------------")
        # print(commit)
        sha = commit["sha"]
        commit_url = f"{base_url}/repos/{repo}/commits/{sha}"
        commit_details = requests.get(commit_url, headers=headers, verify=False)
        # print(commit_details)
        if commit_details.status_code == 200:
            files = commit_details.json().get("files", [])
            print(files)
            for file in files:
                filename_only = file["filename"].split("/")[-1]
                print(filename_only)
                if target_file.lower() in filename_only.lower():
                    full_path = file["filename"]
                    print(f"Found: {full_path} in commit {sha}")
                    content_url = f"{base_url}/repos/{repo}/contents/{full_path}?ref={sha}"
                    content_response = requests.get(content_url, headers=headers, verify=False)
                    if content_response.status_code == 200:
                        content_json = content_response.json()
                        decoded = base64.b64decode(content_json["content"]).decode("utf-8")
                        save_path = os.path.join(os.getcwd(), f"{filename_only}")
                        with open(save_path, "w", encoding="utf-8") as f:
                            f.write(decoded)
                        print(f"\nFile saved as: {save_path}")
                    else:
                        print(f"Found but couldn't fetch the file content: {content_response.status_code}")
                    found = True
                    break
        if found:
            break
    if not found:
        print(f"'{target_file}' not found in the commit")       
else:
    print(f"Failed to fetch commits")
