import yaml
def config_load():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)
    
config = config_load()
jira_config = config['jira']
jira_url = jira_config['jira_server']
email = jira_config['email']
api_token = jira_config['jira_token']
github_config = config['github']
github_token = github_config['github_token']
repo = github_config['github_repo']
base_url = github_config['github_server']
file_config = config["file"]
file_name = file_config["file_name"]
date = config['date']
release_names = config['release_name']
