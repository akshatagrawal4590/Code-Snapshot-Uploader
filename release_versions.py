import requests
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings()
import utils
jira_url = utils.jira_url
email = utils.email
api_token = utils.api_token
release_names = utils.release_names
url = f"https://agile-jira.wellsfargo.net/rest/api/2/version/"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}
all_versions = []
start_at = 0
max_results = 50000
print("Fetching JIRA Issues", end="")
while True:
    params = {
        "startAt": start_at,
        "maxResults": max_results
    }
    print(".", end="")
    response = requests.get(url, headers=headers,params=params,verify=False)
    if response.status_code == 200:
        data = response.json()
        versions = data["values"]
        # print(len(versions))
        all_versions.extend(versions)
        if len(versions) < max_results:
            print("")
            break
        start_at += max_results
        # print(start_at)
all_released_version_ids = []
# print(len(all_versions))
for version in all_versions:
    if version["released"] == True:
        for name in release_names:
            if name in version["name"]:
                all_released_version_ids.append(version["id"])
        
# print(all_released_version_ids)
