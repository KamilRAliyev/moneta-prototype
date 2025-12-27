# Statement File Upload Logic

## Overview

Statement file upload is an **atomic operation** that ensures file storage and database record creation succeed or fail together. The process includes duplicate detection, metadata extraction, and error handling.

## Upload Flow

```mermaid
flowchart TB
    Start[File Upload Request]

    ValidateFile[Validate File:<br/>- CSV extension<br/>- Non-empty<br/>- Size <= 50MB]

    ValidFile{File<br/>Valid?}

    ReadContent[Read File Content]

    VerifyAccount[Verify Account Exists]

    AccountExists{Account<br/>Exists?}

    ComputeHash[Compute SHA-256<br/>Content Hash]

    CheckDuplicate[Check for Duplicate:<br/>Same account_id + content_hash]

    DuplicateFound{Duplicate<br/>Found?}

    GenerateUUID[Generate Statement UUID]

    ExtractMetadata[Extract CSV Metadata:<br/>row_count, columns,<br/>date_from, date_to,<br/>date_column]

    CreateDBRecord[Create StatementFile<br/>DB Record<br/>is_ingested = false<br/>ingested_rows_count = 0<br/>ingestion_errors_count = 0]

    WriteFile["Write File to Disk:<br/>/data/statements/UUID.csv"]

    CommitDB[Commit DB Transaction]

    Success[Return StatementFile<br/>Response]

    Error[Rollback DB<br/>Delete File if Written<br/>Return Error]

    Start --> ValidateFile
    ValidateFile --> ValidFile

    ValidFile -->|No| Error
    ValidFile -->|Yes| ReadContent

    ReadContent --> VerifyAccount
    VerifyAccount --> AccountExists

    AccountExists -->|No| Error
    AccountExists -->|Yes| ComputeHash

    ComputeHash --> CheckDuplicate
    CheckDuplicate --> DuplicateFound

    DuplicateFound -->|Yes| Error
    DuplicateFound -->|No| GenerateUUID

    GenerateUUID --> ExtractMetadata
    ExtractMetadata --> CreateDBRecord
    CreateDBRecord --> WriteFile

    WriteFile --> CommitDB
    CommitDB -->|Success| Success
    CommitDB -->|Failure| Error

    WriteFile -.->|Failure| Error

    style Success fill:#d1fae5,stroke:#059669
    style Error fill:#fee2e2,stroke:#dc2626
```

## Atomic Operation Guarantee

The upload process ensures **atomicity** - either both file and database record are created, or neither:

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant FileSystem
    participant Database

    Client->>API: POST /statements (file)
    API->>Service: create_statement_file()

    Service->>Service: Validate & Extract Metadata
    Service->>Database: Begin Transaction
    Service->>FileSystem: Write File
    FileSystem-->>Service: Success

    alt DB Commit Success
        Service->>Database: Commit Transaction
        Database-->>Service: Success
        Service-->>API: StatementFile Object
        API-->>Client: 201 Created
    else DB Commit Failure
        Service->>FileSystem: Delete File (Rollback)
        Service->>Database: Rollback Transaction
        Service-->>API: DatabaseError
        API-->>Client: 500 Error
    end

    alt File Write Failure
        Service->>Database: Rollback Transaction
        Service-->>API: FileSystemError
        API-->>Client: 500 Error
    end
```

## Duplicate Detection

```mermaid
flowchart TB
    Start[Compute Content Hash]

    Hash[SHA-256 Hash of<br/>File Content]

    QueryDB[Query Database:<br/>WHERE account_id = X<br/>AND content_hash = Y]

    Found{Record<br/>Found?}

    Duplicate[Return 409 Conflict<br/>with Existing Statement Info]

    NoDuplicate[Continue Upload]

    Start --> Hash
    Hash --> QueryDB
    QueryDB --> Found

    Found -->|Yes| Duplicate
    Found -->|No| NoDuplicate

    style Duplicate fill:#fee2e2,stroke:#dc2626
    style NoDuplicate fill:#d1fae5,stroke:#059669
```

**Duplicate Detection Rules:**
- Same file content (hash) uploaded to **same account** → Duplicate
- Same file content uploaded to **different account** → Allowed (different account_id)
- Different file content → Always allowed

## Error Recovery

```mermaid
flowchart TB
    Error[Error Occurs]

    CheckFileWritten{File<br/>Written?}

    CheckDBCommitted{DB<br/>Committed?}

    DeleteFile[Delete File<br/>from Disk]

    RollbackDB[Rollback DB<br/>Transaction]

    LogError[Log Error with<br/>Context]

    ReturnError[Return Error<br/>to Client]

    Error --> CheckFileWritten
    CheckFileWritten -->|Yes| DeleteFile
    CheckFileWritten -->|No| CheckDBCommitted

    DeleteFile --> CheckDBCommitted
    CheckDBCommitted -->|Yes| RollbackDB
    CheckDBCommitted -->|No| LogError

    RollbackDB --> LogError
    LogError --> ReturnError

    style ReturnError fill:#fee2e2,stroke:#dc2626
```

**Error Handling Strategy:**
1. If file written but DB fails → Delete file (cleanup)
2. If DB committed but file write fails → Rollback DB (shouldn't happen, but safe)
3. Log all errors with context for debugging
4. Return appropriate HTTP status codes

## File Storage

**Location:** `/data/statements/{uuid}.csv`

**Naming:** Uses UUID from database record to ensure uniqueness

**Persistence:** Files stored in persistent volume (Docker volume mount)

## Initial State

When a statement file is created, it starts with:

- `is_ingested = false`
- `ingested_rows_count = 0`
- `ingestion_errors_count = 0`
- `ingested_at = null`
- `date_column = <detected column name or null>`

These fields are updated during the ingestion process.

## Related Components

- **Service:** `backend/server/services/statement_file.py` - `create_statement_file` method
- **Router:** `backend/server/api/routers/v1/statements.py` - Upload endpoint
- **Model:** `backend/server/models/statement_file.py` - StatementFile model
- **Schema:** `backend/server/api/schemas/statement_file.py` - Response schemas
