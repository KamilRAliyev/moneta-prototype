/**
 * Account-related TypeScript types matching backend DTOs
 */

export interface Account {
  id: number;
  name: string;
  institution: string;
  currency: string;
  account_type: string;
  economic_area: string | null;
  datelock_from: string | null; // ISO date string (YYYY-MM-DD)
  datelock_to: string | null; // ISO date string (YYYY-MM-DD)
  created_at: string; // ISO datetime string
  updated_at: string | null; // ISO datetime string
}

export interface AccountCreateRequest {
  name: string;
  institution: string;
  currency: string;
  account_type: string;
  economic_area?: string | null;
  datelock_from?: string | null; // ISO date string (YYYY-MM-DD)
  datelock_to?: string | null; // ISO date string (YYYY-MM-DD)
}

export interface AccountUpdateRequest {
  name?: string;
  institution?: string;
  currency?: string;
  account_type?: string;
  economic_area?: string | null;
  datelock_from?: string | null; // ISO date string (YYYY-MM-DD)
  datelock_to?: string | null; // ISO date string (YYYY-MM-DD)
}

export interface AccountTypeOption {
  value: string;
  label: string;
}

export interface EconomicAreaOption {
  value: string;
  label: string;
}

export interface CurrencyOption {
  code: string;
  name: string;
  digits: number;
}

export interface MetaOptionsResponse {
  account_types: AccountTypeOption[];
  economic_areas: EconomicAreaOption[];
  currencies: CurrencyOption[];
}
