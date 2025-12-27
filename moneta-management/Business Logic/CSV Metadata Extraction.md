# CSV Metadata Extraction

## Overview

When a CSV statement file is uploaded, the system automatically extracts metadata including row count, column names, date range, and detects the date column. This metadata is used for display, validation, and later ingestion.

## Extraction Flow

```mermaid
flowchart TB
    Start[CSV File Upload]

    Decode[Decode UTF-8 Content]

    ReadHeader[Read CSV Header Row]

    EmptyFile{File<br/>Empty?}

    Initialize["Initialize:<br/>row_count = 0<br/>date_column_index = None<br/>date_values = empty array"]

    FindDateColumn[Search Header for Date Column<br/>Check: Date, Transaction Date,<br/>Posted Date, date, transaction_date]

    DateColumnFound{Date Column<br/>Found?}

    ReadRows[Read Data Rows]

    CountRow[Increment row_count]

    CollectDate{Date Column<br/>Index Valid?}

    ExtractDate[Extract Date Value<br/>Add to date_values]

    MoreRows{More<br/>Rows?}

    InferFormat[Use dateinfer to Infer<br/>Date Format<br/>Sample: First 100 dates]

    ParseDates[Parse Dates:<br/>1. Try strptime with inferred format<br/>2. Fallback to dateutil parser]

    CalculateRange[Calculate:<br/>date_from = min parsed_dates<br/>date_to = max parsed_dates]

    ReturnMetadata[Return:<br/>row_count, columns,<br/>date_from, date_to,<br/>date_column_name]

    Error[Log Warning<br/>Return Defaults]

    Start --> Decode
    Decode --> ReadHeader

    ReadHeader --> EmptyFile
    EmptyFile -->|Yes| ReturnMetadata
    EmptyFile -->|No| Initialize

    Initialize --> FindDateColumn
    FindDateColumn --> DateColumnFound

    DateColumnFound -->|Yes| ReadRows
    DateColumnFound -->|No| ReadRows

    ReadRows --> CountRow
    CountRow --> CollectDate

    CollectDate -->|Yes| ExtractDate
    CollectDate -->|No| MoreRows

    ExtractDate --> MoreRows
    MoreRows -->|Yes| ReadRows
    MoreRows -->|No| InferFormat

    InferFormat --> ParseDates
    ParseDates --> CalculateRange
    CalculateRange --> ReturnMetadata

    ReadRows -.->|Error| Error
    InferFormat -.->|Error| Error
    ParseDates -.->|Error| Error
    Error --> ReturnMetadata

    style ReturnMetadata fill:#d1fae5,stroke:#059669
    style Error fill:#fee2e2,stroke:#dc2626
```

## Date Column Detection

The system searches for date columns using a predefined list of common names:

```python
date_column_names = [
    "Date",
    "Transaction Date",
    "Posted Date",
    "date",
    "transaction_date",
]
```

**Detection Logic:**
1. Iterate through header columns
2. Check if column name matches any in the list (case-sensitive)
3. Store the first match as `date_column_name`
4. Use its index to extract date values from data rows

**Why Persist `date_column`?**
- Ensures consistent date column usage between upload and ingestion
- Avoids mismatches if CSV has multiple date-like columns
- Makes ingestion deterministic

## Date Format Inference

```mermaid
flowchart LR
    Start[Date Values Array]

    Sample[Take First 100<br/>Date Values]

    Infer[dateinfer.infer<br/>Analyze Patterns]

    GetFormat[Get Inferred<br/>Format String]

    Parse[For Each Date Value:<br/>1. Try strptime with format<br/>2. If fails, use dateutil parser]

    Success{Parse<br/>Success?}

    AddToList[Add to<br/>parsed_dates]

    Calculate[Calculate Range:<br/>min and max dates]

    Start --> Sample
    Sample --> Infer
    Infer --> GetFormat
    GetFormat --> Parse
    Parse --> Success
    Success -->|Yes| AddToList
    Success -->|No| Parse
    AddToList --> Calculate

    style Calculate fill:#d1fae5,stroke:#059669
```

**Inference Strategy:**
1. Use `dateinfer` library to analyze date patterns
2. Sample first 100 date values for performance
3. Get inferred format string (e.g., `"%Y-%m-%d"`)
4. Parse dates using inferred format
5. Fallback to `dateutil.parser` if format parsing fails
6. Calculate min/max for date range

## Error Handling

The extraction process is **non-fatal** - failures don't prevent file upload:

- **Empty file:** Returns `(0, None, None, None, None)`
- **No date column:** Returns `(row_count, columns, None, None, None)`
- **Date parsing failures:** Logs warning, continues with other metadata
- **Format inference failures:** Falls back to dateutil parser

All errors are logged but don't block the upload process.

## Return Values

The `_extract_csv_metadata` method returns:

```python
Tuple[int, Optional[List[str]], Optional[date], Optional[date], Optional[str]]
```

1. **row_count** (int): Number of data rows (excluding header)
2. **columns** (List[str] | None): Array of column names from header
3. **date_from** (date | None): Earliest date found in date column
4. **date_to** (date | None): Latest date found in date column
5. **date_column** (str | None): Name of detected date column

## Example

**Input CSV:**
```csv
Date,Description,Amount
2024-01-01,Coffee,-4.50
2024-01-15,Salary,5000.00
2024-02-01,Rent,-1200.00
```

**Extracted Metadata:**
- `row_count = 3`
- `columns = ["Date", "Description", "Amount"]`
- `date_from = 2024-01-01`
- `date_to = 2024-02-01`
- `date_column = "Date"`

## Related Components

- **Service:** `backend/server/services/statement_file.py` - `_extract_csv_metadata` method
- **Model:** `backend/server/models/statement_file.py` - StatementFile model stores metadata
- **Schema:** `backend/server/api/schemas/statement_file.py` - API response schemas
