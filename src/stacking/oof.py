import pandas as pd
import numpy as np

class TimeSeriesOOF:
    """
    Time-ordered expanding window cross-validator for supply chain metrics.
    Prevents future data leakage in multi-target stacking.
    """
    def __init__(self, date_column='date', n_splits=4):
        self.date_column = date_column
        self.n_splits = n_splits

    def split(self, df: pd.DataFrame):
        dates = pd.to_datetime(df[self.date_column]).sort_values().unique()
        n_dates = len(dates)
        min_train_size = int(n_dates * 0.4)
        step = (n_dates - min_train_size) // self.n_splits

        for i in range(self.n_splits):
            train_end_idx = min_train_size + i * step
            val_end_idx = train_end_idx + step if i < self.n_splits - 1 else n_dates

            train_dates = dates[:train_end_idx]
            val_dates = dates[train_end_idx:val_end_idx]

            train_indices = df[df[self.date_column].isin(train_dates)].index.values
            val_indices = df[df[self.date_column].isin(val_dates)].index.values

            yield train_indices, val_indices