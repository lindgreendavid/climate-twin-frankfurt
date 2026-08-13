export interface GapSummary {
  label: string;
  n_days: number;
  mean_gap_c: number | null;
  ci_95_low: number | null;
  ci_95_high: number | null;
  block_length_days: number | null;
  resamples: number | null;
  seed: number | null;
  gap_excludes_zero: boolean;
}

export interface TrendSummary {
  label: string;
  slope_c_per_year: number | null;
  intercept_c: number | null;
  ci_95_low: number | null;
  ci_95_high: number | null;
  p_value: number | null;
  r_squared: number | null;
  n_years: number;
  alpha: number;
  significant: boolean;
  slope_ci_excludes_zero: boolean;
}

export interface DailyPoint {
  date: string;
  urban_tmk_c: number;
  reference_tmk_c: number;
  gap_c: number;
}

export interface Registry {
  schema_version: number;
  stations: {
    urban: { id: string; name: string };
    reference: { id: string; name: string };
  };
  period: {
    start_date: string;
    end_date: string;
    n_valid_paired_days: number;
  };
  settings: {
    alpha: number;
    bootstrap_resamples: number;
    bootstrap_seed: number;
    block_length_days: number;
    min_valid_days_per_year: number;
  };
  year_coverage: {
    counts: Record<string, number>;
    included_years: string[];
    excluded_years: string[];
  };
  gap: {
    full_period: GapSummary;
    by_season: Record<"DJF" | "MAM" | "JJA" | "SON", GapSummary>;
  };
  trend: TrendSummary;
  annual_means: Record<string, number>;
  daily_series: DailyPoint[];
}
