"""Data Transformation Agent - format, encode, normalize, scale."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field


@dataclass
class TransformReport:
    """Report of transformation operations."""
    transformations: List[str] = field(default_factory=list)
    columns_added: List[str] = field(default_factory=list)
    columns_removed: List[str] = field(default_factory=list)
    columns_modified: List[str] = field(default_factory=list)


class TransformAgent:
    """AI-powered data transformation agent."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_df = df.copy()
        self.report = TransformReport()

    def normalize(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'minmax'
    ) -> 'TransformAgent':
        """
        Normalize numeric columns.

        Methods:
        - 'minmax': Scale to 0-1 range
        - 'zscore': Standardize to mean=0, std=1
        - 'robust': Use median and IQR (robust to outliers)
        """
        cols = columns or self.df.select_dtypes(include=[np.number]).columns.tolist()

        for col in cols:
            if method == 'minmax':
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                if max_val != min_val:
                    self.df[col] = (self.df[col] - min_val) / (max_val - min_val)
            elif method == 'zscore':
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                if std_val != 0:
                    self.df[col] = (self.df[col] - mean_val) / std_val
            elif method == 'robust':
                median_val = self.df[col].median()
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr != 0:
                    self.df[col] = (self.df[col] - median_val) / iqr

            self.report.columns_modified.append(col)
            self.report.transformations.append(f"Normalized '{col}' using {method}")

        return self

    def encode_categorical(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'label'
    ) -> 'TransformAgent':
        """
        Encode categorical columns.

        Methods:
        - 'label': Label encoding (0, 1, 2, ...)
        - 'onehot': One-hot encoding
        - 'binary': Binary encoding for high cardinality
        - 'frequency': Frequency encoding
        """
        cols = columns or self.df.select_dtypes(include=['object', 'category']).columns.tolist()

        for col in cols:
            if method == 'label':
                unique_values = self.df[col].unique()
                mapping = {v: i for i, v in enumerate(unique_values)}
                self.df[col] = self.df[col].map(mapping)
                self.report.transformations.append(f"Label encoded '{col}' ({len(mapping)} categories)")

            elif method == 'onehot':
                dummies = pd.get_dummies(self.df[col], prefix=col, dtype=int)
                self.df = pd.concat([self.df.drop(col, axis=1), dummies], axis=1)
                self.report.columns_removed.append(col)
                self.report.columns_added.extend(dummies.columns.tolist())
                self.report.transformations.append(f"One-hot encoded '{col}' ({len(dummies.columns)} new columns)")

            elif method == 'frequency':
                freq = self.df[col].value_counts(normalize=True)
                self.df[col] = self.df[col].map(freq)
                self.report.transformations.append(f"Frequency encoded '{col}'")

            elif method == 'binary':
                unique_values = self.df[col].unique()
                n_bits = int(np.ceil(np.log2(len(unique_values) + 1)))
                mapping = {v: i for i, v in enumerate(unique_values)}

                for i in range(n_bits):
                    self.df[f"{col}_bit{i}"] = self.df[col].map(mapping).apply(lambda x: (x >> i) & 1)
                    self.report.columns_added.append(f"{col}_bit{i}")

                self.df = self.df.drop(col, axis=1)
                self.report.columns_removed.append(col)
                self.report.transformations.append(f"Binary encoded '{col}' ({n_bits} bits)")

            self.report.columns_modified.append(col)

        return self

    def create_features(
        self,
        date_column: Optional[str] = None,
        numeric_interactions: bool = False
    ) -> 'TransformAgent':
        """Create new features from existing data."""

        # Date features
        if date_column and date_column in self.df.columns:
            try:
                date_col = pd.to_datetime(self.df[date_column], errors='coerce')

                self.df[f'{date_column}_year'] = date_col.dt.year
                self.df[f'{date_column}_month'] = date_col.dt.month
                self.df[f'{date_column}_day'] = date_col.dt.day
                self.df[f'{date_column}_dayofweek'] = date_col.dt.dayofweek
                self.df[f'{date_column}_quarter'] = date_col.dt.quarter

                new_cols = [f'{date_column}_{x}' for x in ['year', 'month', 'day', 'dayofweek', 'quarter']]
                self.report.columns_added.extend(new_cols)
                self.report.transformations.append(f"Created date features from '{date_column}'")
            except Exception as e:
                pass

        # Numeric interactions
        if numeric_interactions:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                for i, col1 in enumerate(numeric_cols[:3]):  # Limit to first 3
                    for col2 in numeric_cols[i+1:4]:
                        # Ratio
                        if (self.df[col2] != 0).all():
                            ratio_col = f'{col1}_div_{col2}'
                            self.df[ratio_col] = self.df[col1] / self.df[col2]
                            self.report.columns_added.append(ratio_col)

                        # Product
                        prod_col = f'{col1}_x_{col2}'
                        self.df[prod_col] = self.df[col1] * self.df[col2]
                        self.report.columns_added.append(prod_col)

                self.report.transformations.append("Created numeric interaction features")

        return self

    def bin_numeric(
        self,
        column: str,
        bins: Union[int, List[float]] = 5,
        labels: Optional[List[str]] = None
    ) -> 'TransformAgent':
        """Bin numeric column into categories."""
        if column not in self.df.columns:
            return self

        new_col = f'{column}_binned'
        self.df[new_col] = pd.cut(self.df[column], bins=bins, labels=labels)

        self.report.columns_added.append(new_col)
        self.report.transformations.append(f"Binned '{column}' into {bins if isinstance(bins, int) else len(bins)-1} categories")

        return self

    def aggregate(
        self,
        group_by: Union[str, List[str]],
        agg_dict: Dict[str, Union[str, List[str]]]
    ) -> 'TransformAgent':
        """Aggregate data by group."""
        self.df = self.df.groupby(group_by).agg(agg_dict).reset_index()

        # Flatten column names if multi-level
        if isinstance(self.df.columns, pd.MultiIndex):
            self.df.columns = ['_'.join(col).strip('_') for col in self.df.columns]

        self.report.transformations.append(f"Aggregated by {group_by}")

        return self

    def pivot(
        self,
        index: str,
        columns: str,
        values: str,
        aggfunc: str = 'mean'
    ) -> 'TransformAgent':
        """Pivot the DataFrame."""
        self.df = pd.pivot_table(
            self.df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc
        ).reset_index()

        self.report.transformations.append(f"Pivoted data: index={index}, columns={columns}")

        return self

    def rename_columns(self, mapping: Dict[str, str]) -> 'TransformAgent':
        """Rename columns."""
        self.df = self.df.rename(columns=mapping)
        self.report.transformations.append(f"Renamed {len(mapping)} columns")
        return self

    def drop_columns(self, columns: List[str]) -> 'TransformAgent':
        """Drop specified columns."""
        existing = [c for c in columns if c in self.df.columns]
        self.df = self.df.drop(columns=existing)
        self.report.columns_removed.extend(existing)
        self.report.transformations.append(f"Dropped {len(existing)} columns")
        return self

    def select_columns(self, columns: List[str]) -> 'TransformAgent':
        """Select only specified columns."""
        existing = [c for c in columns if c in self.df.columns]
        dropped = [c for c in self.df.columns if c not in existing]
        self.df = self.df[existing]
        self.report.columns_removed.extend(dropped)
        self.report.transformations.append(f"Selected {len(existing)} columns")
        return self

    def sort(
        self,
        by: Union[str, List[str]],
        ascending: bool = True
    ) -> 'TransformAgent':
        """Sort DataFrame."""
        self.df = self.df.sort_values(by=by, ascending=ascending)
        self.report.transformations.append(f"Sorted by {by}")
        return self

    def filter_rows(
        self,
        column: str,
        condition: str,
        value: Any
    ) -> 'TransformAgent':
        """
        Filter rows based on condition.

        Conditions: '==', '!=', '>', '<', '>=', '<=', 'in', 'not in', 'contains'
        """
        before = len(self.df)

        if condition == '==':
            self.df = self.df[self.df[column] == value]
        elif condition == '!=':
            self.df = self.df[self.df[column] != value]
        elif condition == '>':
            self.df = self.df[self.df[column] > value]
        elif condition == '<':
            self.df = self.df[self.df[column] < value]
        elif condition == '>=':
            self.df = self.df[self.df[column] >= value]
        elif condition == '<=':
            self.df = self.df[self.df[column] <= value]
        elif condition == 'in':
            self.df = self.df[self.df[column].isin(value)]
        elif condition == 'not in':
            self.df = self.df[~self.df[column].isin(value)]
        elif condition == 'contains':
            self.df = self.df[self.df[column].str.contains(value, na=False)]

        after = len(self.df)
        self.report.transformations.append(f"Filtered rows: {before} -> {after}")

        return self

    def get_result(self) -> pd.DataFrame:
        """Get the transformed DataFrame."""
        return self.df

    def get_report(self) -> TransformReport:
        """Get the transformation report."""
        return self.report

    def get_report_dict(self) -> Dict[str, Any]:
        """Get report as dictionary."""
        return {
            'transformations': self.report.transformations,
            'columns_added': self.report.columns_added,
            'columns_removed': self.report.columns_removed,
            'columns_modified': self.report.columns_modified,
            'final_shape': f"{len(self.df)} x {len(self.df.columns)}"
        }
