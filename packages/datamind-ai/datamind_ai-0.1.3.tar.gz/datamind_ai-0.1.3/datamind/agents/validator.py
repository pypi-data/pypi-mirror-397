"""Data Validation Agent - schema, rules, quality checks."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    level: ValidationLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Complete validation report."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    results: List[ValidationResult] = field(default_factory=list)
    score: float = 0.0  # 0-100


class ValidatorAgent:
    """AI-powered data validation agent."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.report = ValidationReport()
        self.rules: List[Dict[str, Any]] = []

    def _add_result(self, result: ValidationResult):
        """Add a validation result."""
        self.report.results.append(result)
        self.report.total_checks += 1

        if result.passed:
            self.report.passed += 1
        elif result.level == ValidationLevel.WARNING:
            self.report.warnings += 1
        else:
            self.report.failed += 1

    def check_not_null(
        self,
        columns: Optional[List[str]] = None,
        threshold: float = 0.0
    ) -> 'ValidatorAgent':
        """Check that columns don't have null values (or below threshold)."""
        cols = columns or self.df.columns.tolist()

        for col in cols:
            null_ratio = self.df[col].isnull().mean()
            passed = null_ratio <= threshold

            self._add_result(ValidationResult(
                name=f"not_null_{col}",
                passed=passed,
                level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
                message=f"Column '{col}' null check: {null_ratio*100:.1f}% nulls (threshold: {threshold*100:.1f}%)",
                details={'column': col, 'null_ratio': null_ratio, 'threshold': threshold}
            ))

        return self

    def check_unique(
        self,
        columns: List[str],
        should_be_unique: bool = True
    ) -> 'ValidatorAgent':
        """Check if column(s) have unique values."""
        if isinstance(columns, str):
            columns = [columns]

        if len(columns) == 1:
            is_unique = self.df[columns[0]].nunique() == len(self.df)
        else:
            is_unique = self.df.duplicated(subset=columns).sum() == 0

        passed = is_unique == should_be_unique

        self._add_result(ValidationResult(
            name=f"unique_{'_'.join(columns)}",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Columns {columns} uniqueness: {'unique' if is_unique else 'has duplicates'}",
            details={'columns': columns, 'is_unique': is_unique}
        ))

        return self

    def check_range(
        self,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> 'ValidatorAgent':
        """Check if numeric column values are within range."""
        if column not in self.df.columns:
            return self

        violations = 0
        actual_min = self.df[column].min()
        actual_max = self.df[column].max()

        if min_value is not None:
            violations += (self.df[column] < min_value).sum()
        if max_value is not None:
            violations += (self.df[column] > max_value).sum()

        passed = violations == 0

        self._add_result(ValidationResult(
            name=f"range_{column}",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Column '{column}' range check: {violations} violations (range: {min_value}-{max_value}, actual: {actual_min}-{actual_max})",
            details={
                'column': column,
                'violations': int(violations),
                'expected_range': [min_value, max_value],
                'actual_range': [actual_min, actual_max]
            }
        ))

        return self

    def check_values(
        self,
        column: str,
        allowed_values: List[Any]
    ) -> 'ValidatorAgent':
        """Check if column values are in allowed list."""
        if column not in self.df.columns:
            return self

        invalid = ~self.df[column].isin(allowed_values)
        invalid_count = invalid.sum()
        invalid_values = self.df[column][invalid].unique().tolist()[:10]

        passed = invalid_count == 0

        self._add_result(ValidationResult(
            name=f"values_{column}",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Column '{column}' allowed values check: {invalid_count} invalid values",
            details={
                'column': column,
                'invalid_count': int(invalid_count),
                'invalid_values': invalid_values,
                'allowed_values': allowed_values
            }
        ))

        return self

    def check_pattern(
        self,
        column: str,
        pattern: str,
        description: str = ""
    ) -> 'ValidatorAgent':
        """Check if column values match regex pattern."""
        if column not in self.df.columns:
            return self

        matches = self.df[column].astype(str).str.match(pattern, na=False)
        non_matching = (~matches).sum()

        passed = non_matching == 0

        self._add_result(ValidationResult(
            name=f"pattern_{column}",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Column '{column}' pattern check ({description}): {non_matching} non-matching values",
            details={
                'column': column,
                'pattern': pattern,
                'non_matching_count': int(non_matching)
            }
        ))

        return self

    def check_dtype(
        self,
        column: str,
        expected_dtype: str
    ) -> 'ValidatorAgent':
        """Check column data type."""
        if column not in self.df.columns:
            return self

        actual_dtype = str(self.df[column].dtype)

        # Flexible dtype matching
        dtype_groups = {
            'numeric': ['int64', 'int32', 'float64', 'float32', 'int', 'float'],
            'string': ['object', 'string', 'str'],
            'datetime': ['datetime64[ns]', 'datetime64', 'datetime'],
            'boolean': ['bool', 'boolean'],
            'category': ['category']
        }

        if expected_dtype in dtype_groups:
            passed = actual_dtype in dtype_groups[expected_dtype]
        else:
            passed = actual_dtype == expected_dtype

        self._add_result(ValidationResult(
            name=f"dtype_{column}",
            passed=passed,
            level=ValidationLevel.WARNING if not passed else ValidationLevel.INFO,
            message=f"Column '{column}' dtype: expected {expected_dtype}, got {actual_dtype}",
            details={
                'column': column,
                'expected_dtype': expected_dtype,
                'actual_dtype': actual_dtype
            }
        ))

        return self

    def check_row_count(
        self,
        min_rows: Optional[int] = None,
        max_rows: Optional[int] = None
    ) -> 'ValidatorAgent':
        """Check if row count is within expected range."""
        row_count = len(self.df)

        passed = True
        if min_rows is not None and row_count < min_rows:
            passed = False
        if max_rows is not None and row_count > max_rows:
            passed = False

        self._add_result(ValidationResult(
            name="row_count",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Row count: {row_count} (expected: {min_rows}-{max_rows})",
            details={
                'row_count': row_count,
                'min_rows': min_rows,
                'max_rows': max_rows
            }
        ))

        return self

    def check_column_exists(self, columns: List[str]) -> 'ValidatorAgent':
        """Check if required columns exist."""
        existing = set(self.df.columns)
        missing = [c for c in columns if c not in existing]

        passed = len(missing) == 0

        self._add_result(ValidationResult(
            name="required_columns",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Required columns check: {len(missing)} missing columns",
            details={
                'required': columns,
                'missing': missing,
                'existing': list(existing)
            }
        ))

        return self

    def check_no_duplicates(
        self,
        columns: Optional[List[str]] = None
    ) -> 'ValidatorAgent':
        """Check for duplicate rows."""
        if columns:
            dup_count = self.df.duplicated(subset=columns).sum()
        else:
            dup_count = self.df.duplicated().sum()

        passed = dup_count == 0

        self._add_result(ValidationResult(
            name="no_duplicates",
            passed=passed,
            level=ValidationLevel.WARNING if not passed else ValidationLevel.INFO,
            message=f"Duplicate check: {dup_count} duplicate rows found",
            details={
                'duplicate_count': int(dup_count),
                'columns': columns or 'all'
            }
        ))

        return self

    def check_referential_integrity(
        self,
        column: str,
        reference_df: pd.DataFrame,
        reference_column: str
    ) -> 'ValidatorAgent':
        """Check if all values in column exist in reference."""
        reference_values = set(reference_df[reference_column].unique())
        invalid = ~self.df[column].isin(reference_values)
        invalid_count = invalid.sum()

        passed = invalid_count == 0

        self._add_result(ValidationResult(
            name=f"referential_{column}",
            passed=passed,
            level=ValidationLevel.ERROR if not passed else ValidationLevel.INFO,
            message=f"Referential integrity '{column}': {invalid_count} orphan records",
            details={
                'column': column,
                'invalid_count': int(invalid_count)
            }
        ))

        return self

    def check_custom(
        self,
        name: str,
        condition: Callable[[pd.DataFrame], bool],
        message: str,
        level: ValidationLevel = ValidationLevel.ERROR
    ) -> 'ValidatorAgent':
        """Add custom validation check."""
        try:
            passed = condition(self.df)
        except Exception as e:
            passed = False
            message = f"{message} (Error: {str(e)})"

        self._add_result(ValidationResult(
            name=name,
            passed=passed,
            level=level if not passed else ValidationLevel.INFO,
            message=message
        ))

        return self

    def validate_schema(self, schema: Dict[str, Dict[str, Any]]) -> 'ValidatorAgent':
        """
        Validate against a schema definition.

        Schema format:
        {
            'column_name': {
                'dtype': 'numeric',
                'nullable': False,
                'unique': False,
                'min': 0,
                'max': 100,
                'allowed_values': [1, 2, 3],
                'pattern': r'^\d{4}-\d{2}-\d{2}$'
            }
        }
        """
        # Check required columns
        required_cols = list(schema.keys())
        self.check_column_exists(required_cols)

        for col, rules in schema.items():
            if col not in self.df.columns:
                continue

            # Data type check
            if 'dtype' in rules:
                self.check_dtype(col, rules['dtype'])

            # Nullable check
            if 'nullable' in rules and not rules['nullable']:
                self.check_not_null([col])

            # Unique check
            if rules.get('unique', False):
                self.check_unique([col])

            # Range check
            if 'min' in rules or 'max' in rules:
                self.check_range(col, rules.get('min'), rules.get('max'))

            # Allowed values check
            if 'allowed_values' in rules:
                self.check_values(col, rules['allowed_values'])

            # Pattern check
            if 'pattern' in rules:
                self.check_pattern(col, rules['pattern'])

        return self

    def run_all_checks(self) -> 'ValidatorAgent':
        """Run all standard validation checks."""
        # Check for nulls
        self.check_not_null(threshold=0.5)  # Warning if >50% nulls

        # Check for duplicates
        self.check_no_duplicates()

        # Check row count
        self.check_row_count(min_rows=1)

        # Check each column
        for col in self.df.columns:
            # Check dtype makes sense
            if self.df[col].dtype == 'object':
                # Check for empty strings
                empty_count = (self.df[col] == '').sum()
                if empty_count > 0:
                    self._add_result(ValidationResult(
                        name=f"empty_strings_{col}",
                        passed=False,
                        level=ValidationLevel.WARNING,
                        message=f"Column '{col}' has {empty_count} empty strings",
                        details={'column': col, 'empty_count': int(empty_count)}
                    ))

        return self

    def get_report(self) -> ValidationReport:
        """Get the validation report."""
        # Calculate score
        if self.report.total_checks > 0:
            self.report.score = (self.report.passed / self.report.total_checks) * 100

        return self.report

    def get_report_dict(self) -> Dict[str, Any]:
        """Get report as dictionary."""
        report = self.get_report()
        return {
            'score': round(report.score, 1),
            'total_checks': report.total_checks,
            'passed': report.passed,
            'failed': report.failed,
            'warnings': report.warnings,
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'level': r.level.value,
                    'message': r.message
                }
                for r in report.results
            ]
        }

    def is_valid(self) -> bool:
        """Check if all validations passed (no errors)."""
        return self.report.failed == 0
