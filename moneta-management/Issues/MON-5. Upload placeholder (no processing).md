**As a user**,
I want to upload a CSV file,
So that ingestion plumbing can be tested.

**Acceptance criteria**
- POST /api/v1/uploads
- File saved to /data/uploads/{uuid}.csv
- No parsing or validation yet
- Response returns file ID + path