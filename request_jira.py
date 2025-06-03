import requests
import urllib3
from release_versions import all_released_version_ids
urllib3.disable_warnings()
import utils
from datetime import datetime
def get_prod_versions(url, headers, version_ids):
    all_prod_versions = []
    for version in version_ids:
        # print(version)
        version_url = f"{url}/{version}"  
        response = requests.get(version_url, headers=headers,verify=False)
        if response.status_code == 200:
            data = response.json()
            all_prod_versions.append(data)
    
    return all_prod_versions
def get_release_dates(prod_versions):
    release_data = []
    for version in prod_versions:
        # Filering based on target date
        target_date = datetime.strptime(utils.date, "%Y-%m-%d")
        releaseDate = datetime.strptime(version["releaseDate"], "%Y-%m-%d")
        if releaseDate <= target_date:
            release_data.append({"id": version["id"], "releaseDate": version["releaseDate"], "name": version["name"]})
    release_data = sorted(release_data, key = lambda x: x["releaseDate"], reverse = True)
    # print(release_data)
    return release_data
def get_issue_with_file_change(releaseData, issuesData, file_name):
    for release in releaseData:
        for item in issuesData[release["name"]]:
            ids = [i for i in item]
            for id in ids:
                # print(id)
                if id["notes"] == None:
                    # print("Skip")
                    continue
                if file_name in id["notes"]:
                    res_str = f"{file_name} found with -> Key: {id["key"]}  Release: {release["name"]}  Release Date: {release["releaseDate"]}"
                    print(res_str)
                    return id["key"],release["name"],release["releaseDate"]
                
def get_issues_for_version(release_data, api_token):
    url = f"https://agile-jira.wellsfargo.net/rest/api/2/search/"
    headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
    }
    issues = {}
    for release in release_data:
        fixVersionId = release["id"]
        params = {
            "jql": f'fixVersion="{fixVersionId}"'
        }
        response = requests.get(url, headers=headers,params=params,verify=False)
        if response.status_code == 200:
            data = response.json()
            data = data.get("issues", [])
            # print(f"issues in fixversion: {release["name"]}")
            for issue in data:
                key = issue["key"]
                summary = issue["fields"]["summary"]
                status = issue["fields"]["status"]
                notes = issue["fields"]["customfield_10602"]
                issues.setdefault(f"{release["name"]}", []).append([{"key": key, "summary": summary, "status": status, "notes": notes}])
    return issues
def runner_for_all_file(file_name,api_token,prod_versions):
    url = f"https://agile-jira.wellsfargo.net/rest/api/2/version"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    prod_verions_data = get_prod_versions(url, headers, prod_versions)
    releaseData = get_release_dates(prod_verions_data)
    # print(releaseData)
    issuesData = get_issues_for_version(releaseData, api_token)
    print("\t\t|")
    print("\t\t-->", end="")
    story_number = get_issue_with_file_change(releaseData, issuesData, file_name)
    if story_number == None:
        return "No Story for this file in any Release version Found!!",file_name
    return story_number[0],file_name
def main():
    jira_url = utils.jira_url
    email = utils.email
    api_token = utils.api_token
    prod_versions = all_released_version_ids
    story_with_file = []
    
    for file in utils.file_name:
        story,file = runner_for_all_file(file,api_token,prod_versions)
        story_with_file.append({"story": story, "file": file})
    return story_with_file
      
if __name__ == "__main__":
    main()
