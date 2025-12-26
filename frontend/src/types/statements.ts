/**
 * Statement-related TypeScript types matching backend DTOs
 */

export interface StatementFile {
  id: string; // UUID
  account_id: number;
  account_name?: string | null;
  original_filename: string;
  stored_filename: string;
  stored_path: string;
  format: string;
  size_bytes: number;
  content_hash: string;
  row_count: number;
  columns: string[] | null;
  date_from: string | null; // ISO date string (YYYY-MM-DD)
  date_to: string | null; // ISO date string (YYYY-MM-DD)
  status: string;
  is_ingested: boolean;
  ingested_at: string | null; // ISO datetime string
  file_exists: boolean; // Whether the file exists on disk
  created_at: string; // ISO datetime string
  updated_at: string | null; // ISO datetime string
}

export interface StatementFileSummary {
  id: string; // UUID
  account_id: number;
  account_name?: string | null;
  original_filename: string;
  size_bytes: number;
  row_count: number;
  date_from: string | null; // ISO date string (YYYY-MM-DD)
  date_to: string | null; // ISO date string (YYYY-MM-DD)
  status: string;
  is_ingested: boolean;
  ingested_at: string | null; // ISO datetime string
  file_exists: boolean; // Whether the file exists on disk
  created_at: string; // ISO datetime string
}

export interface DuplicateStatementFileResponse {
  detail: string;
  existing_statement_id: string; // UUID
  existing_created_at: string; // ISO datetime string
}

export interface DetectedFormat {
  strptime_format: string;
  human_readable: string;
  confidence: number;
  matches: number;
  total_tested: number;
}

export interface DateFormatInferenceResponse {
  date_column_detected: boolean;
  date_column_name: string | null;
  date_column_index: number | null;
  inferred_format: DetectedFormat | null;
  date_range: {
    earliest: string; // ISO date string
    latest: string; // ISO date string
  } | null;
  total_rows_analyzed: number;
  parsing_errors: number;
  sample_dates: string[];
}

export interface DateFormatOption {
  format: string;
  pattern: string;
  description: string;
  example: string;
}

export interface SupportedDateFormatsResponse {
  supported_formats: DateFormatOption[];
}
