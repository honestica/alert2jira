# alert2jira

## What is it made for
alert2jira transforms json notification into JIRA issue (task for now).

For now, the input is limited to grafana 8 (legacy) alert notification but it will be able to manage new grafana alerting or prometheus alertmanager without a lot of work.

## Routes

List and explanations of routes

| Route             | Method | Details                                                                                                          |
|-------------------|--------|------------------------------------------------------------------------------------------------------------------|
| /docs             | GET    | swagger ui                                                                                                       |
| /liveness         | GET    | Liveness probe that checks that the server is up                                                                 |
| /readiness        | GET    | Checks that JIRA server is OK                                                                                    |
| /dummy            | POST   | Returns and logs any payload passed to it.<br>Useful when you don't know what the sent payload looks like.      |
| /grafana8-mock    | POST   | Wants a legacy grafana alert json and return JIRA issue JSON.<br>Created for automated testing                  |
| /grafana8-webhook | POST   | Wants a legacy grafana alert json and creates a JIRA issue                                                       |

## ENV VAR

To connect to JIRA, we need `JIRA_API_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`

To create a JIRA issue, we need `JIRA_PROJECT_KEY`