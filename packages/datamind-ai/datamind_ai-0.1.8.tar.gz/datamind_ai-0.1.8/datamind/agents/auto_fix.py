"""AI Auto-Fix Agent - automatically diagnose and fix data issues."""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
import os
import json


@dataclass
class FixAction:
    """A single fix action."""
    issue: str
    action: str
    column: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    applied: bool = False


@dataclass
class AutoFixReport:
    """Report of auto-fix operations."""
    issues_found: List[str] = field(default_factory=list)
    fixes_applied: List[FixAction] = field(default_factory=list)
    fixes_skipped: List[FixAction] = field(default_factory=list)
    ai_recommendations: List[str] = field(default_factory=list)


class AutoFixAgent:
    """AI-powered auto-fix agent that diagnoses and fixes data issues."""

    def __init__(self, df: pd.DataFrame, use_ai: bool = True):
        self.df = df.copy()
        self.original_df = df.copy()
        self.report = AutoFixReport()
        self.use_ai = use_ai
        self._ai_analyzer = None

    def _get_ai_analyzer(self):
        """Get AI analyzer (lazy loading)."""
        if self._ai_analyzer is None and self.use_ai:
            try:
                if os.environ.get('GROQ_API_KEY'):
                    from datamind.ai.groq_ai import GroqAnalyzer
                    self._ai_analyzer = GroqAnalyzer()
                elif os.environ.get('GEMINI_API_KEY'):
                    from datamind.ai.gemini import GeminiAnalyzer
                    self._ai_analyzer = GeminiAnalyzer()
            except:
                pass
        return self._ai_analyzer

    def diagnose(self) -> Dict[str, Any]:
        """Run comprehensive diagnosis on the data."""
        issues = {
            'shape': {'rows': len(self.df), 'columns': len(self.df.columns)},
            'duplicates': self._diagnose_duplicates(),
            'missing': self._diagnose_missing(),
            'outliers': self._diagnose_outliers(),
            'dtypes': self._diagnose_dtypes(),
            'quality_score': 0
        }

        # Calculate quality score
        score = 100
        if issues['duplicates']['count'] > 0:
            score -= min(20, issues['duplicates']['percentage'])
        if issues['missing']['total_percentage'] > 0:
            score -= min(30, issues['missing']['total_percentage'])
        if issues['outliers']['total_count'] > 0:
            score -= min(20, issues['outliers']['total_count'] / len(self.df) * 100)
        if len(issues['dtypes']['suggestions']) > 0:
            score -= len(issues['dtypes']['suggestions']) * 5

        issues['quality_score'] = max(0, round(score, 1))

        return issues

    def _diagnose_duplicates(self) -> Dict[str, Any]:
        """Diagnose duplicate rows."""
        dup_count = self.df.duplicated().sum()
        return {
            'count': int(dup_count),
            'percentage': round(dup_count / len(self.df) * 100, 2) if len(self.df) > 0 else 0
        }

    def _diagnose_missing(self) -> Dict[str, Any]:
        """Diagnose missing values."""
        missing = self.df.isnull().sum()
        missing_cols = {col: int(val) for col, val in missing.items() if val > 0}
        total = missing.sum()

        return {
            'by_column': missing_cols,
            'total': int(total),
            'total_percentage': round(total / self.df.size * 100, 2) if self.df.size > 0 else 0
        }

    def _diagnose_outliers(self) -> Dict[str, Any]:
        """Diagnose outliers in numeric columns."""
        outliers = {}
        total = 0

        for col in self.df.select_dtypes(include=[np.number]).columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            outlier_count = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
            if outlier_count > 0:
                outliers[col] = {
                    'count': int(outlier_count),
                    'bounds': [round(lower, 2), round(upper, 2)]
                }
                total += outlier_count

        return {
            'by_column': outliers,
            'total_count': int(total)
        }

    def _diagnose_dtypes(self) -> Dict[str, Any]:
        """Diagnose data type issues."""
        current = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        suggestions = {}

        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                # Check if numeric
                try:
                    numeric = pd.to_numeric(self.df[col], errors='coerce')
                    if numeric.notna().mean() > 0.8:
                        suggestions[col] = 'numeric'
                        continue
                except:
                    pass

                # Check if datetime
                try:
                    datetime_col = pd.to_datetime(self.df[col], errors='coerce')
                    if datetime_col.notna().mean() > 0.8:
                        suggestions[col] = 'datetime'
                except:
                    pass

        return {
            'current': current,
            'suggestions': suggestions
        }

    def auto_fix(
        self,
        fix_duplicates: bool = True,
        fix_missing: bool = True,
        fix_outliers: bool = True,
        fix_dtypes: bool = True,
        missing_strategy: str = 'auto',
        outlier_strategy: str = 'clip'
    ) -> 'AutoFixAgent':
        """Automatically fix all detected issues."""

        diagnosis = self.diagnose()

        # 1. Fix duplicates
        if fix_duplicates and diagnosis['duplicates']['count'] > 0:
            self._fix_duplicates()

        # 2. Fix missing values
        if fix_missing and diagnosis['missing']['total'] > 0:
            self._fix_missing(strategy=missing_strategy)

        # 3. Fix outliers
        if fix_outliers and diagnosis['outliers']['total_count'] > 0:
            self._fix_outliers(strategy=outlier_strategy)

        # 4. Fix data types
        if fix_dtypes and len(diagnosis['dtypes']['suggestions']) > 0:
            self._fix_dtypes(diagnosis['dtypes']['suggestions'])

        return self

    def _fix_duplicates(self) -> None:
        """Fix duplicate rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)

        if removed > 0:
            action = FixAction(
                issue=f"{removed} duplicate rows found",
                action=f"Removed {removed} duplicate rows",
                applied=True
            )
            self.report.fixes_applied.append(action)
            self.report.issues_found.append(f"Duplicates: {removed} rows")

    def _fix_missing(self, strategy: str = 'auto') -> None:
        """Fix missing values."""
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count == 0:
                continue

            self.report.issues_found.append(f"Missing values in '{col}': {missing_count}")

            if strategy == 'auto':
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    fill_value = self.df[col].median()
                    method = 'median'
                else:
                    mode = self.df[col].mode()
                    fill_value = mode[0] if len(mode) > 0 else ''
                    method = 'mode'
            elif strategy == 'mean':
                fill_value = self.df[col].mean()
                method = 'mean'
            elif strategy == 'median':
                fill_value = self.df[col].median()
                method = 'median'
            elif strategy == 'mode':
                mode = self.df[col].mode()
                fill_value = mode[0] if len(mode) > 0 else ''
                method = 'mode'
            elif strategy == 'drop':
                self.df = self.df.dropna(subset=[col])
                action = FixAction(
                    issue=f"Missing values in '{col}'",
                    action=f"Dropped {missing_count} rows",
                    column=col,
                    applied=True
                )
                self.report.fixes_applied.append(action)
                continue
            else:
                continue

            self.df[col] = self.df[col].fillna(fill_value)
            action = FixAction(
                issue=f"Missing values in '{col}'",
                action=f"Filled with {method} ({fill_value})",
                column=col,
                details={'method': method, 'value': str(fill_value)},
                applied=True
            )
            self.report.fixes_applied.append(action)

    def _fix_outliers(self, strategy: str = 'clip') -> None:
        """Fix outliers in numeric columns."""
        for col in self.df.select_dtypes(include=[np.number]).columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            outlier_mask = (self.df[col] < lower) | (self.df[col] > upper)
            outlier_count = outlier_mask.sum()

            if outlier_count == 0:
                continue

            self.report.issues_found.append(f"Outliers in '{col}': {outlier_count}")

            if strategy == 'clip':
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                action_desc = f"Clipped to [{lower:.2f}, {upper:.2f}]"
            elif strategy == 'remove':
                self.df = self.df[~outlier_mask]
                action_desc = f"Removed {outlier_count} rows"
            elif strategy == 'median':
                median_val = self.df[col].median()
                self.df.loc[outlier_mask, col] = median_val
                action_desc = f"Replaced with median ({median_val:.2f})"
            else:
                continue

            action = FixAction(
                issue=f"Outliers in '{col}'",
                action=action_desc,
                column=col,
                details={'count': int(outlier_count), 'strategy': strategy},
                applied=True
            )
            self.report.fixes_applied.append(action)

    def _fix_dtypes(self, suggestions: Dict[str, str]) -> None:
        """Fix data type issues."""
        for col, suggested_type in suggestions.items():
            if col not in self.df.columns:
                continue

            self.report.issues_found.append(f"Type issue in '{col}': should be {suggested_type}")

            try:
                if suggested_type == 'numeric':
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                elif suggested_type == 'datetime':
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

                action = FixAction(
                    issue=f"Type issue in '{col}'",
                    action=f"Converted to {suggested_type}",
                    column=col,
                    applied=True
                )
                self.report.fixes_applied.append(action)
            except Exception as e:
                action = FixAction(
                    issue=f"Type issue in '{col}'",
                    action=f"Failed to convert: {str(e)}",
                    column=col,
                    applied=False
                )
                self.report.fixes_skipped.append(action)

    def get_ai_recommendations(self) -> List[str]:
        """Get AI recommendations for data improvement."""
        analyzer = self._get_ai_analyzer()
        if not analyzer:
            return ["AI analyzer not available"]

        try:
            diagnosis = self.diagnose()
            sample = self.df.head(10).to_string()

            prompt = f"""
Data diagnosis qilindi. Quyidagi muammolar topildi:

DIAGNOSIS:
- Shape: {diagnosis['shape']}
- Duplicates: {diagnosis['duplicates']}
- Missing: {diagnosis['missing']}
- Outliers: {diagnosis['outliers']}
- Quality Score: {diagnosis['quality_score']}/100

SAMPLE DATA:
{sample}

Data sifatini yaxshilash uchun 3-5 ta qisqa tavsiya ber (o'zbek tilida).
Har bir tavsiyani yangi qatordan boshla.
"""
            response = analyzer._chat(prompt)
            recommendations = [r.strip() for r in response.strip().split('\n') if r.strip()]
            self.report.ai_recommendations = recommendations[:5]
            return recommendations[:5]
        except Exception as e:
            return [f"AI recommendation error: {str(e)}"]

    def get_result(self) -> pd.DataFrame:
        """Get the fixed DataFrame."""
        return self.df

    def get_report(self) -> AutoFixReport:
        """Get the fix report."""
        return self.report

    def get_report_dict(self) -> Dict[str, Any]:
        """Get report as dictionary."""
        return {
            'issues_found': self.report.issues_found,
            'fixes_applied': [
                {
                    'issue': f.issue,
                    'action': f.action,
                    'column': f.column
                }
                for f in self.report.fixes_applied
            ],
            'fixes_skipped': [
                {
                    'issue': f.issue,
                    'action': f.action,
                    'column': f.column
                }
                for f in self.report.fixes_skipped
            ],
            'ai_recommendations': self.report.ai_recommendations,
            'original_shape': f"{len(self.original_df)} x {len(self.original_df.columns)}",
            'final_shape': f"{len(self.df)} x {len(self.df.columns)}"
        }

    def compare(self) -> Dict[str, Any]:
        """Compare original and fixed data."""
        return {
            'original': {
                'rows': len(self.original_df),
                'columns': len(self.original_df.columns),
                'missing': int(self.original_df.isnull().sum().sum()),
                'duplicates': int(self.original_df.duplicated().sum())
            },
            'fixed': {
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'missing': int(self.df.isnull().sum().sum()),
                'duplicates': int(self.df.duplicated().sum())
            },
            'changes': {
                'rows_removed': len(self.original_df) - len(self.df),
                'missing_fixed': int(self.original_df.isnull().sum().sum() - self.df.isnull().sum().sum()),
                'duplicates_removed': int(self.original_df.duplicated().sum() - self.df.duplicated().sum())
            }
        }
