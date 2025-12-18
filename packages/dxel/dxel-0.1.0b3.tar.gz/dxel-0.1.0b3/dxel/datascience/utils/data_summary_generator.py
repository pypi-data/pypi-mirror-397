
import pandas as pd
import numpy as np
import re
from scipy import stats

def clean_str_series(s: pd.Series) -> pd.Series:
    """Convert series to string type and strip whitespace."""
    return s.astype("string").str.strip()

def is_na_token(value: str) -> bool:
    """Check if a value represents a missing/null token."""
    return str(value).lower() in {"", "na", "n/a", "none", "null", "nan", "missing", "?", "-"}

def detect_boolean(s: pd.Series, min_conf: float):
    """Detect if series contains boolean values and map them."""
    true_tokens = {"true", "t", "1", "yes", "y"}
    false_tokens = {"false", "f", "0", "no", "n"}
    x = s.dropna().str.lower()
    ok = x.isin(true_tokens | false_tokens)
    frac = ok.mean() if len(x) else 0.0
    if frac >= min_conf:
        mapped = x.map({**{k: True for k in true_tokens},
                        **{k: False for k in false_tokens}})
        return True, mapped
    return False, None

def detect_numeric(s: pd.Series, min_conf: float):
    """Detect if series contains numeric values, handling currency and percentages."""
    num_cleaner = re.compile(r"[,\s_]")
    currency = re.compile(r"^[\$\€\£\¥]")
    x = s.dropna().str.replace(num_cleaner, "", regex=True)
    x = x.str.replace(currency, "", regex=True)
    has_pct = s.dropna().str.endswith("%")
    x = x.str.rstrip("%")
    nums = pd.to_numeric(x, errors="coerce")
    frac = nums.notna().mean() if len(nums) else 0.0
    pct_frac = has_pct.mean() if len(has_pct) else 0.0
    return frac >= min_conf, nums, pct_frac

def is_integer_series(nums: pd.Series, min_conf: float):
    """Check if a numeric series contains primarily integer values."""
    non_null = nums.dropna()
    if len(non_null) == 0:
        return False
    # Convert to float first to ensure is_integer works properly
    mask = non_null.astype(float).apply(lambda x: float.is_integer(x))
    return mask.mean() >= min_conf

def detect_datetime(s: pd.Series, min_conf: float):
    """Detect if a series contains datetime values."""
    dt = pd.to_datetime(s.dropna(), errors="coerce")
    frac = dt.notna().mean() if len(dt) else 0.0
    return frac >= min_conf, dt

def summarize_numeric(x: pd.Series):
    """Calculate statistical summary for numeric series."""
    if x.notna().sum() == 0:
        return {"non_null_count": 0}
    
    summary = {
        "non_null_count": int(x.notna().sum()),
        "minimum_value": float(np.nanmin(x)),
        "percentile_25": float(np.nanpercentile(x, 25)),
        "median_value": float(np.nanmedian(x)),
        "percentile_75": float(np.nanpercentile(x, 75)),
        "maximum_value": float(np.nanmax(x)),
        "mean_average": float(np.nanmean(x)),
        "standard_deviation": float(np.nanstd(x, ddof=1)) if x.notna().sum() > 1 else 0.0,
    }
    
    # Add outlier detection
    outlier_info = detect_outliers_iqr(x)
    if outlier_info["outlier_count"] > 0:
        summary["outlier_analysis"] = outlier_info
    
    # Add skewness and kurtosis if available
    skew_info = detect_skewness(x)
    if skew_info:
        summary["distribution_shape"] = skew_info
    
    # Add zeros count
    zero_count = (x == 0).sum()
    if zero_count > 0:
        summary["zero_values"] = {
            "zero_count": int(zero_count),
            "zero_percentage": round(float(zero_count / len(x) * 100), 4)
        }
    
    return summary

def summarize_bool(x: pd.Series):
    """Calculate value counts for boolean series."""
    vc = x.value_counts(dropna=False)
    return {str(k): int(v) for k, v in vc.items()}

def summarize_categorical(s: pd.Series, k=5):
    """Summarize categorical series with unique count and top values."""
    vc = s.value_counts(dropna=True)
    top = [{"category_value": str(idx), "frequency_count": int(cnt)} for idx, cnt in vc.head(k).items()]
    return {
        "unique_value_count": int(s.nunique(dropna=True)), 
        "most_frequent_values": top
    }

def get_dataframe_overview(df: pd.DataFrame):
    """Get comprehensive DataFrame metadata and overview."""
    memory_usage = df.memory_usage(deep=True)
    
    return {
        "dataset_shape": {
            "total_rows": int(df.shape[0]),
            "total_columns": int(df.shape[1])
        },
        "memory_usage_analysis": {
            "total_bytes": int(memory_usage.sum()),
            "total_megabytes": round(memory_usage.sum() / (1024**2), 4),
            "memory_per_column_bytes": {col: int(mem) for col, mem in memory_usage.items() if col != 'Index'}
        },
        "duplicate_rows": {
            "duplicate_count": int(df.duplicated().sum()),
            "duplicate_percentage": round(df.duplicated().sum() / len(df) * 100, 4) if len(df) > 0 else 0.0
        },
        "missing_data_summary": {
            "total_missing_cells": int(df.isna().sum().sum()),
            "total_cells_in_dataset": int(df.shape[0] * df.shape[1]),
            "overall_missing_percentage": round(df.isna().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 4) if df.shape[0] * df.shape[1] > 0 else 0.0
        }
    }

def detect_outliers_iqr(x: pd.Series):
    """Detect outliers using IQR method for numeric series."""
    if x.notna().sum() == 0:
        return {"outlier_count": 0, "outlier_percentage": 0.0}
    
    q1 = np.nanpercentile(x, 25)
    q3 = np.nanpercentile(x, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = ((x < lower_bound) | (x > upper_bound)) & x.notna()
    outlier_count = int(outliers.sum())
    
    return {
        "outlier_count": outlier_count,
        "outlier_percentage": round(outlier_count / x.notna().sum() * 100, 4) if x.notna().sum() > 0 else 0.0,
        "iqr_lower_bound": float(lower_bound),
        "iqr_upper_bound": float(upper_bound)
    }

def detect_skewness(x: pd.Series):
    
    return {
        "skewness": round(float(stats.skew(x.dropna())), 4),
        "kurtosis": round(float(stats.kurtosis(x.dropna())), 4)
    }

def analyze_text_patterns(s: pd.Series):
    """Analyze patterns in text data."""
    non_null = s.dropna()
    if len(non_null) == 0:
        return {}
    
    lengths = non_null.astype(str).str.len()
    
    # Check for common patterns
    has_numbers = non_null.astype(str).str.contains(r'\d', regex=True).sum()
    has_special_chars = non_null.astype(str).str.contains(r'[^a-zA-Z0-9\s]', regex=True).sum()
    has_emails = non_null.astype(str).str.contains(r'@', regex=True).sum()
    has_urls = non_null.astype(str).str.contains(r'http|www', regex=True, case=False).sum()
    
    return {
        "text_length_statistics": {
            "minimum_length": int(lengths.min()),
            "maximum_length": int(lengths.max()),
            "average_length": round(float(lengths.mean()), 2),
            "median_length": float(lengths.median())
        },
        "content_patterns_detected": {
            "entries_with_numbers": int(has_numbers),
            "entries_with_special_characters": int(has_special_chars),
            "entries_with_email_format": int(has_emails),
            "entries_with_urls": int(has_urls)
        }
    }

def get_correlation_info(df: pd.DataFrame, column: str, threshold: float = 0.5):
    """Get correlation information for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if column not in numeric_cols or len(numeric_cols) < 2:
        return None
    
    correlations = df[numeric_cols].corr()[column].drop(column)
    high_corr = correlations[abs(correlations) >= threshold].sort_values(ascending=False)
    
    if len(high_corr) == 0:
        return None
    
    return {
        "highly_correlated_columns": [
            {"correlated_column_name": col, "correlation_coefficient": round(float(corr), 4)}
            for col, corr in high_corr.items()
        ]
    }

# === Main Function ===

def summarize_df(df: pd.DataFrame, min_conf: float = 0.95, top_k: int = 5, include_correlations: bool = True):
    """
    Analyze DataFrame columns and infer their types with statistical summaries.
    
    Args:
        df: Input DataFrame to analyze
        min_conf: Minimum confidence threshold (0-1) for type inference
        top_k: Number of top values to show for categorical columns
        return_json: If True, return JSON string; otherwise return dict
        include_correlations: If True, include correlation analysis for numeric columns
        
    Returns:
        JSON string or dict containing type inference and summary for each column
    """
    # Start with DataFrame overview
    result = {
        "dataset_overview": get_dataframe_overview(df),
        "column_analysis": {}
    }

    for col in df.columns:
        s = clean_str_series(df[col])
        na_mask = s.isna() | s.map(is_na_token)
        s_clean = s.mask(na_mask)

        n = len(s)
        n_missing = int(na_mask.sum())
        pct_missing = float(n_missing / n) if n else 0.0
        n_nonmissing = n - n_missing

        col_info = {
            "data_type": None,
            "has_missing_values": bool(n_missing > 0),
            "missing_value_count": n_missing,
            "missing_value_percentage": round(pct_missing * 100, 4),
        }

        # 1. Boolean
        is_bool, mapped_bool = detect_boolean(s_clean, min_conf)
        if is_bool:
            col_info["data_type"] = "boolean"
            col_info["statistical_summary"] = {"value_distribution": summarize_bool(mapped_bool)}
            result["column_analysis"][col] = col_info
            continue

        # 2. Numeric (integer / float / percentage)
        is_num, nums, pct_frac = detect_numeric(s_clean, min_conf)
        if is_num:
            if is_integer_series(nums, min_conf):
                col_info["data_type"] = "integer"
                col_info["statistical_summary"] = summarize_numeric(nums.astype("Int64"))
            elif pct_frac >= min_conf:
                col_info["data_type"] = "percentage"
                col_info["statistical_summary"] = summarize_numeric(nums.astype(float) / 100.0)
            else:
                col_info["data_type"] = "float"
                col_info["statistical_summary"] = summarize_numeric(nums.astype(float))
            
            # Add correlation info for numeric columns
            if include_correlations:
                corr_info = get_correlation_info(df, col)
                if corr_info:
                    col_info["correlation_analysis"] = corr_info
            
            result["column_analysis"][col] = col_info
            continue

        # 3. Datetime
        is_dt, dt = detect_datetime(s_clean, min_conf)
        if is_dt:
            col_info["data_type"] = "datetime"
            col_info["statistical_summary"] = {
                "non_null_count": int(dt.notna().sum()),
                "earliest_date": str(dt.min()) if dt.notna().any() else None,
                "latest_date": str(dt.max()) if dt.notna().any() else None,
            }
            result["column_analysis"][col] = col_info
            continue

        # 4. Categorical / Text
        nunique = s_clean.nunique(dropna=True)
        uniq_ratio = float(nunique / max(n_nonmissing, 1)) if n_nonmissing else 0.0
        inferred = "categorical" if (nunique <= 50 or uniq_ratio <= 0.2) else "text"
        col_info["data_type"] = inferred
        if inferred == "categorical":
            col_info["statistical_summary"] = summarize_categorical(s_clean, k=top_k)
        else:
            text_analysis = analyze_text_patterns(s_clean)
            col_info["statistical_summary"] = {
                "unique_value_count": int(nunique),
                "sample_values": [str(v) for v in s_clean.dropna().unique()[:top_k]]
            }
            if text_analysis:
                col_info["text_pattern_analysis"] = text_analysis
        result["column_analysis"][col] = col_info

    return result


