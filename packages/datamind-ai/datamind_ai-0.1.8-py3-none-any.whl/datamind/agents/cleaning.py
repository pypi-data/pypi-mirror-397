"""Data Cleaning Agent - dublikatlar, missing values, outliers."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class CleaningReport:
    """Report of cleaning operations performed."""
    original_rows: int = 0
    original_cols: int = 0
    final_rows: int = 0
    final_cols: int = 0
    duplicates_removed: int = 0
    missing_filled: Dict[str, int] = field(default_factory=dict)
    outliers_handled: Dict[str, int] = field(default_factory=dict)
    issues_found: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)


class CleaningAgent:
    """AI-powered data cleaning agent."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_df = df.copy()
        self.report = CleaningReport(
            original_rows=len(df),
            original_cols=len(df.columns)
        )

    def diagnose(self) -> Dict[str, Any]:
        """Diagnose all data quality issues."""
        issues = {
            'duplicates': self._check_duplicates(),
            'missing_values': self._check_missing(),
            'outliers': self._check_outliers(),
            'data_types': self._check_dtypes(),
            'inconsistencies': self._check_inconsistencies(),
        }
        return issues

    def _check_duplicates(self) -> Dict[str, Any]:
        """Check for duplicate rows."""
        dup_count = self.df.duplicated().sum()
        dup_rows = self.df[self.df.duplicated(keep=False)]
        return {
            'count': int(dup_count),
            'percentage': round(dup_count / len(self.df) * 100, 2) if len(self.df) > 0 else 0,
            'sample': dup_rows.head(5).to_dict() if dup_count > 0 else {}
        }

    def _check_missing(self) -> Dict[str, Any]:
        """Check for missing values."""
        missing = self.df.isnull().sum()
        missing_dict = {col: int(val) for col, val in missing.items() if val > 0}
        return {
            'by_column': missing_dict,
            'total': int(missing.sum()),
            'percentage': round(missing.sum() / self.df.size * 100, 2) if self.df.size > 0 else 0
        }

    def _check_outliers(self) -> Dict[str, Any]:
        """Check for outliers using IQR method."""
        outliers = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            outlier_mask = (self.df[col] < lower) | (self.df[col] > upper)
            outlier_count = outlier_mask.sum()

            if outlier_count > 0:
                outliers[col] = {
                    'count': int(outlier_count),
                    'percentage': round(outlier_count / len(self.df) * 100, 2),
                    'lower_bound': round(lower, 2),
                    'upper_bound': round(upper, 2),
                    'min_value': round(self.df[col].min(), 2),
                    'max_value': round(self.df[col].max(), 2)
                }

        return outliers

    def _check_dtypes(self) -> Dict[str, Any]:
        """Check for potential data type issues."""
        issues = {}

        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                # Check if it could be numeric
                try:
                    numeric_conversion = pd.to_numeric(self.df[col], errors='coerce')
                    valid_count = numeric_conversion.notna().sum()
                    if valid_count > len(self.df) * 0.8:  # 80% can be converted
                        issues[col] = {
                            'current_type': 'object',
                            'suggested_type': 'numeric',
                            'convertible_percentage': round(valid_count / len(self.df) * 100, 2)
                        }
                except:
                    pass

                # Check if it could be datetime
                try:
                    date_conversion = pd.to_datetime(self.df[col], errors='coerce')
                    valid_count = date_conversion.notna().sum()
                    if valid_count > len(self.df) * 0.8:
                        issues[col] = {
                            'current_type': 'object',
                            'suggested_type': 'datetime',
                            'convertible_percentage': round(valid_count / len(self.df) * 100, 2)
                        }
                except:
                    pass

        return issues

    def _check_inconsistencies(self) -> Dict[str, Any]:
        """Check for inconsistent values in categorical columns."""
        issues = {}

        for col in self.df.select_dtypes(include=['object']).columns:
            values = self.df[col].dropna().unique()

            # Check for leading/trailing whitespace
            whitespace_issues = [v for v in values if isinstance(v, str) and v != v.strip()]

            # Check for case inconsistencies
            lower_values = [str(v).lower() for v in values]
            if len(lower_values) != len(set(lower_values)):
                case_issues = True
            else:
                case_issues = False

            if whitespace_issues or case_issues:
                issues[col] = {
                    'whitespace_issues': len(whitespace_issues),
                    'case_inconsistencies': case_issues,
                    'unique_values': len(values)
                }

        return issues

    def remove_duplicates(self, keep: str = 'first') -> 'CleaningAgent':
        """Remove duplicate rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates(keep=keep)
        removed = before - len(self.df)

        self.report.duplicates_removed = removed
        if removed > 0:
            self.report.actions_taken.append(f"Removed {removed} duplicate rows")

        return self

    def fill_missing(
        self,
        strategy: str = 'auto',
        columns: Optional[List[str]] = None,
        fill_value: Any = None
    ) -> 'CleaningAgent':
        """
        Fill missing values.

        Strategies:
        - 'auto': AI decides (mean for numeric, mode for categorical)
        - 'mean': Fill with mean (numeric only)
        - 'median': Fill with median (numeric only)
        - 'mode': Fill with most frequent value
        - 'ffill': Forward fill
        - 'bfill': Backward fill
        - 'value': Fill with specific value
        - 'drop': Drop rows with missing values
        """
        cols = columns or self.df.columns.tolist()

        for col in cols:
            if self.df[col].isnull().sum() == 0:
                continue

            missing_count = self.df[col].isnull().sum()

            if strategy == 'drop':
                self.df = self.df.dropna(subset=[col])
                self.report.missing_filled[col] = int(missing_count)
                self.report.actions_taken.append(f"Dropped {missing_count} rows with missing '{col}'")
                continue

            if strategy == 'value' and fill_value is not None:
                self.df[col] = self.df[col].fillna(fill_value)
            elif strategy == 'auto':
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                else:
                    mode_val = self.df[col].mode()
                    if len(mode_val) > 0:
                        self.df[col] = self.df[col].fillna(mode_val[0])
            elif strategy == 'mean' and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif strategy == 'median' and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].median())
            elif strategy == 'mode':
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col] = self.df[col].fillna(mode_val[0])
            elif strategy == 'ffill':
                self.df[col] = self.df[col].ffill()
            elif strategy == 'bfill':
                self.df[col] = self.df[col].bfill()

            filled = missing_count - self.df[col].isnull().sum()
            if filled > 0:
                self.report.missing_filled[col] = int(filled)
                self.report.actions_taken.append(f"Filled {filled} missing values in '{col}' using {strategy}")

        return self

    def handle_outliers(
        self,
        strategy: str = 'clip',
        columns: Optional[List[str]] = None,
        threshold: float = 1.5
    ) -> 'CleaningAgent':
        """
        Handle outliers.

        Strategies:
        - 'clip': Clip values to bounds
        - 'remove': Remove outlier rows
        - 'median': Replace with median
        - 'mean': Replace with mean
        """
        cols = columns or self.df.select_dtypes(include=[np.number]).columns.tolist()

        for col in cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR

            outlier_mask = (self.df[col] < lower) | (self.df[col] > upper)
            outlier_count = outlier_mask.sum()

            if outlier_count == 0:
                continue

            if strategy == 'clip':
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
            elif strategy == 'remove':
                self.df = self.df[~outlier_mask]
            elif strategy == 'median':
                median_val = self.df[col].median()
                self.df.loc[outlier_mask, col] = median_val
            elif strategy == 'mean':
                mean_val = self.df[col].mean()
                self.df.loc[outlier_mask, col] = mean_val

            self.report.outliers_handled[col] = int(outlier_count)
            self.report.actions_taken.append(f"Handled {outlier_count} outliers in '{col}' using {strategy}")

        return self

    def fix_inconsistencies(self, columns: Optional[List[str]] = None) -> 'CleaningAgent':
        """Fix common inconsistencies in text columns."""
        cols = columns or self.df.select_dtypes(include=['object']).columns.tolist()

        for col in cols:
            # Strip whitespace
            if self.df[col].dtype == 'object':
                before = self.df[col].copy()
                self.df[col] = self.df[col].str.strip()

                changes = (before != self.df[col]).sum()
                if changes > 0:
                    self.report.actions_taken.append(f"Stripped whitespace from {changes} values in '{col}'")

        return self

    def convert_dtypes(self, conversions: Optional[Dict[str, str]] = None) -> 'CleaningAgent':
        """Convert column data types."""
        if conversions is None:
            # Auto-detect conversions
            dtype_issues = self._check_dtypes()
            conversions = {col: info['suggested_type'] for col, info in dtype_issues.items()}

        for col, dtype in conversions.items():
            if col not in self.df.columns:
                continue

            try:
                if dtype == 'numeric':
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                elif dtype == 'datetime':
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                elif dtype == 'string':
                    self.df[col] = self.df[col].astype(str)
                elif dtype == 'category':
                    self.df[col] = self.df[col].astype('category')

                self.report.actions_taken.append(f"Converted '{col}' to {dtype}")
            except Exception as e:
                self.report.issues_found.append(f"Failed to convert '{col}' to {dtype}: {str(e)}")

        return self

    def auto_clean(self) -> 'CleaningAgent':
        """Automatically clean data based on detected issues."""
        # 1. Remove duplicates
        self.remove_duplicates()

        # 2. Fix inconsistencies
        self.fix_inconsistencies()

        # 3. Fill missing values
        self.fill_missing(strategy='auto')

        # 4. Handle outliers
        self.handle_outliers(strategy='clip')

        # 5. Convert data types
        self.convert_dtypes()

        return self

    def get_result(self) -> pd.DataFrame:
        """Get the cleaned DataFrame."""
        self.report.final_rows = len(self.df)
        self.report.final_cols = len(self.df.columns)
        return self.df

    def get_report(self) -> CleaningReport:
        """Get the cleaning report."""
        self.report.final_rows = len(self.df)
        self.report.final_cols = len(self.df.columns)
        return self.report

    def get_report_dict(self) -> Dict[str, Any]:
        """Get report as dictionary."""
        report = self.get_report()
        return {
            'original_shape': f"{report.original_rows} x {report.original_cols}",
            'final_shape': f"{report.final_rows} x {report.final_cols}",
            'rows_removed': report.original_rows - report.final_rows,
            'duplicates_removed': report.duplicates_removed,
            'missing_filled': report.missing_filled,
            'outliers_handled': report.outliers_handled,
            'actions_taken': report.actions_taken,
            'issues_found': report.issues_found
        }
