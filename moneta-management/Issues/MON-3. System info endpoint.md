As a developer,
I want a system endpoint to inspect runtime state,
So that I can debug deployments easily.

**Acceptance criteria**
- GET /api/system/info returns:
    - app version
    - environment
    - database connected: true/false
- Also widget in frontend that shows that the info about backend system info