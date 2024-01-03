import datetime
from fastapi import FastAPI, HTTPException, Body
import logging
import os
from pydantic import BaseModel
import requests
from typing import Any

app = FastAPI()
loglevel = os.environ.get('LOGLEVEL')
jira_url = os.environ.get('JIRA_API_URL')
jira_username = os.environ.get('JIRA_USERNAME')
jira_api_token = os.environ.get('JIRA_API_TOKEN')
excluded_endpoints = ['/liveness','/readiness']

def logger(log):
    message='{"@timestamp":"%s","message":"%s"}' % (datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z"), log)
    return message

class EndpointFilter(logging.Filter):
    def __init__(self, excluded_endpoints: list[str]) -> None:
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] not in self.excluded_endpoints

class Grafana8Notification(BaseModel):
    title: str
    message: str

if loglevel != "DEBUG":
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter(excluded_endpoints))


@app.get('/liveness')
async def liveness():
    if not all([jira_url, jira_username, jira_api_token]):
        print(logger("Jira environment variables are not properly set"))
        raise HTTPException(status_code=500, detail='Jira environment variables are not properly set')
    
    return {'status': 'OK'}

@app.get('/readiness')
async def readiness():
    jira_url = os.environ.get('JIRA_API_URL')
    jira_username = os.environ.get('JIRA_USERNAME')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    
    if check_jira_api_health(jira_url, jira_username, jira_api_token):
        return {'status': 'OK'}
    else:
        raise HTTPException(status_code=503, detail='Jira API is not healthy')

@app.post('/dummy')
async def dummy_webhook(payload: Any = Body(None)):
    print(payload)
    return payload

@app.post('/grafana8-mock')
async def grafana8_mock(notification: Grafana8Notification):
    summary = notification.dict()['title']
    description = notification.dict()['message']
    return create_jira_issue(summary,description)

@app.post('/grafana8-webhook')
async def grafana8_webhook(notification: Grafana8Notification):
    summary = notification.dict()['title']
    description = notification.dict()['message']
    send_jira_issue(summary,description)
    return {'message': 'Webhook received successfully'}

def check_jira_api_health(jira_url, jira_username, jira_api_token):
    try:
        url = f"{jira_url}/rest/api/2/myself"
        response = requests.get(
            url,
            auth=(jira_username, jira_api_token),
            timeout=5
        )

        if 200 <= response.status_code < 300:
            if loglevel == "DEBUG":
                print(logger("Jira API is healthy"))
            return True
        else:
            print(f"Jira API returned a non-success status code: {response.status_code}")
            return False
    except Exception as e:
        print(logger("Failed to connect to Jira API: %s" % e))
        return False
    
def create_jira_issue(summary,description,jira_project_key=None):
    if not jira_project_key:
        jira_project_key = os.environ.get('JIRA_PROJECT_KEY')
        if loglevel == "DEBUG":
            print(logger("Using LOGLEVEL env var for JIRA_PROJECT_KEY"))
    if loglevel == "DEBUG":
        print(logger("Summary: %s,\nDescription: %s,\nJIRA project: %s" % (summary, description, jira_project_key)))
    if not jira_project_key:
        raise ValueError("JIRA_PROJECT_KEY must be set")
    issue_data = {
        'fields': {
            'project': {'key': jira_project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'id': '3'},
        }
    }
    if loglevel == "DEBUG":
        print(logger(issue_data))
    return issue_data
    
def send_jira_issue(summary,description,jira_project_key=None):
    jira_payload = create_jira_issue(summary,description)
    if not (jira_url and jira_username and jira_api_token):
        raise ValueError("JIRA_API_URL, JIRA_USERNAME, JIRA_API_TOKEN must be set.")
    response = requests.post(
        f'{jira_url}/rest/api/2/issue/',
        json=jira_payload,
        auth=(jira_username, jira_api_token),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 201:
        print(logger("Jira issue created successfully"))
    else:
        print(logger("Failed to create Jira issue. Status code: %s, Error: %s" % (response.status_code, response.text)))


if __name__ == '__main__':
    app.run()
