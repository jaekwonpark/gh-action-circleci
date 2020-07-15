import urllib.parse

import pandas as pd
import requests, base64
import os

CIRCLE_API = "https://circleci.canaveral-corp.us-west-2.aws/api/v1.1"
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']


def latest_commit(repository, branch=None):
    if branch is None:
        branch = default_branch(repository)
    url = f"https://api.github.com/repos/{repository}/commits"
    response = requests.get(url, params={"sha": branch, "access_token": GITHUB_TOKEN})
    info = "%s (%s)" % (response.reason, response.status_code)
    assert response.status_code == 200, info
    json = response.json()
    commit = json[0]["commit"]
    return commit


def latest_workflow(repository, circle_token="", status="completed",
                    branch=None):
    if branch is None:
        branch = default_branch(repository)
    # CircleCI API requires url-encoded branch
    branch = urllib.parse.quote_plus(branch)
    url = CIRCLE_API + f"/project/github/{repository}/tree"
    url += f"/{branch}?circle-token={circle_token}&filter={status}"
    response = requests.get(url)
    info = "%s (%s)" % (response.reason, response.status_code)
    assert response.status_code == 200, info
    integration_tests = response.json()
    assert integration_tests, "no integration tests found"
    keys = ["workflow_id", "workflow_name", "job_name"]

    records = []
    for test in integration_tests:
        record = test["workflows"]
        record = {key: record[key] for key in keys}
        record["status"] = test["status"]
        records.append(record)
    df, key = pd.DataFrame(records), "workflow_id"
    workflows, workflow_id = df.groupby(key, sort=False), df[key][0]
    workflow = workflows.get_group(workflow_id)
    return workflow


def project_build(repository, github_token="", circle_token="", branch=None):
    """
    if branch is None:
        branch = default_branch(repository, github_token)
    # CircleCI API requires url-encoded branch
    branch = urllib.parse.quote_plus(branch)
    """
    branch = "develop"
    url = CIRCLE_API
    url += f"/project/github/{repository}/tree/"+branch

    userPass = circle_token+":"
    userPassBytes = userPass.encode("ascii")
    b64Val = base64.b64encode(userPassBytes)
    print("auth header:%s"% userPass)
    print("base64:%s"% b64Val)
    print("url:%s"% url)
    headers = {
      "Authorization": "Basic %s" % b64Val,
      "Content-Type": "application/json",
      "Accept": "application/json"
    }
    response = requests.post(url,
            headers=headers,
            data={})
    info = "%s %s (%s)" % (userPass, response.reason, response.status_code)
    assert response.status_code == 200, info
    return response.json()["body"]

"""

def project_build(repository, github_token="", circle_token="", branch=None):
    if branch is None:
        branch = default_branch(repository, github_token)
    # CircleCI API requires url-encoded branch
    branch = urllib.parse.quote_plus(branch)
    url = CIRCLE_API
    url += f"/project/github/{repository}/build?circle-token={circle_token}"
    response = requests.post(url, data={"branch": branch})
    info = "%s (%s)" % (response.reason, response.status_code)
    assert response.status_code == 200, info
    return response.json()["body"]
"""

def default_branch(repository, github_token):
    url = f"https://api.github.com/repos/{repository}"
    response = requests.get(url, params={"access_token": github_token})
    info = f"{repository} not found:"+response.url
    assert response.status_code == 200, info
    data = response.json()
    return data['default_branch']
