"""Data loading utilities for various file formats."""

import pandas as pd
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()


class DataLoader:
    """Load data from various file formats."""

    SUPPORTED_FORMATS = {
        '.csv': 'CSV',
        '.xlsx': 'Excel',
        '.xls': 'Excel',
        '.json': 'JSON',
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        """Load data from file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Fayl topilmadi: {self.file_path}")

        suffix = self.file_path.suffix.lower()

        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Qo'llab-quvvatlanmaydigan format: {suffix}\n"
                f"Qo'llab-quvvatlanadigan formatlar: {list(self.SUPPORTED_FORMATS.keys())}"
            )

        loaders = {
            '.csv': self._load_csv,
            '.xlsx': self._load_excel,
            '.xls': self._load_excel,
            '.json': self._load_json,
        }

        self.df = loaders[suffix]()
        return self.df

    def _load_csv(self) -> pd.DataFrame:
        """Load CSV file."""
        return pd.read_csv(self.file_path)

    def _load_excel(self) -> pd.DataFrame:
        """Load Excel file."""
        return pd.read_excel(self.file_path)

    def _load_json(self) -> pd.DataFrame:
        """Load JSON file."""
        return pd.read_json(self.file_path)

    def get_info(self) -> dict:
        """Get basic information about the loaded data."""
        if self.df is None:
            raise ValueError("Data yuklanmagan. Avval load() ni chaqiring.")

        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'column_names': list(self.df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'missing_values': self.df.isnull().sum().to_dict(),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024:.2f} KB",
        }

    def get_summary(self) -> dict:
        """Get statistical summary of the data."""
        if self.df is None:
            raise ValueError("Data yuklanmagan. Avval load() ni chaqiring.")

        summary = {
            'numeric_summary': {},
            'categorical_summary': {},
        }

        # Numeric columns
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = self.df[numeric_cols].describe().to_dict()

        # Categorical columns
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            summary['categorical_summary'][col] = {
                'unique_count': self.df[col].nunique(),
                'top_values': self.df[col].value_counts().head(5).to_dict(),
            }

        return summary


def load_data(file_path: str) -> tuple[pd.DataFrame, dict]:
    """Convenience function to load data and get info."""
    loader = DataLoader(file_path)
    df = loader.load()
    info = loader.get_info()
    return df, info
