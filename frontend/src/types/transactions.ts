/**
 * Transaction-related TypeScript types matching backend DTOs
 */

export interface StatementFileSummary {
  id: string; // UUID
  original_filename: string;
  columns: string[] | null;
}

export interface AccountSummary {
  id: number;
  name: string;
  institution: string;
  currency: string;
  type: string;
  economic_area: string | null;
  datelock_from: string | null; // ISO date string
  datelock_to: string | null; // ISO date string
}

export interface Transaction {
  id: string; // UUID
  row_id: number;
  statement_file: StatementFileSummary;
  account: AccountSummary;
  ingested_content: Record<string, unknown>; // Dynamic JSON content
  computed_content: Record<string, unknown>;
  inserted_at: string; // ISO datetime string
}

export interface TransactionListResponse {
  items: Transaction[];
  meta: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

export interface TransactionColumnMeta {
  name: string;
  type: "date" | "number" | "string";
  sample_values: string[];
  nullable: boolean;
  min: unknown | null;
  max: unknown | null;
}

export interface TransactionMetaResponse {
  ingested_columns: TransactionColumnMeta[];
  computed_columns: TransactionColumnMeta[];
}

export interface DeleteTransactionsResponse {
  deleted_count: number;
}
