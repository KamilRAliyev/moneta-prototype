
## User Story
**As a user**,
I want to upload statement CSV files,
So that they can later be parsed and fed into transactions.

## Acceptance Criteria
- `statement_files` table exists
- Fields:
  - id (uuid)
  - account_id (fk)
  - original_filename
  - stored_path
  - size_bytes
  - content_hash
  - status
  - created_at
- API:
  - `POST /api/v1/accounts/{account_id}/statements`
- Files stored at `/data/statements/{uuid}.csv`
- Duplicate file detection via `content_hash`
- Status set to `uploaded`

## Out of Scope
- Parsing
- Transaction creation
