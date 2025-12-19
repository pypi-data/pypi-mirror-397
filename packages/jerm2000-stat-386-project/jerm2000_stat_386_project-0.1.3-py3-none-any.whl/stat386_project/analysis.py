from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DEFAULT_CANDIDATES = [
    Path("data/combined_leaders_2025.csv"),  # works when running from repo root
]

def load_combined(path: Path | str | None = None) -> pd.DataFrame:
    if path is None:
        for p in DEFAULT_CANDIDATES:
            if p.exists():
                return pd.read_csv(p)
        raise FileNotFoundError(
            "Could not find combined_leaders_2025.csv. "
            "Pass `path=...` or generate the file first."
        )
    return pd.read_csv(path)

def prepare_data(df: pd.DataFrame, min_hr: int = 5, dropna_cols: Iterable[str] | None = None,) -> pd.DataFrame:
    if dropna_cols is None:
        dropna_cols = [
            'avg_hr_distance',
            'max_hr_distance',
            'avg_launch_speed',
            'max_launch_speed',
            'barrels',
            'brl_percent',
        ]
    df = df.copy()
    df = df[df['hr_count'] >= min_hr]
    df = df.dropna(subset=list(dropna_cols))

    return df

def longest_vs_avg_distance(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    # table comparing longest HR vs average HR distance

    cols = [
        'player_name',
        'hr_count',
        'avg_hr_distance',
        'max_hr_distance',
        'avg_launch_speed',
        'max_launch_speed',
    ]

    subset = df[cols].sort_values("max_hr_distance", ascending=False)
    return subset.head(n)

def correlation_table(df: pd.DataFrame) -> pd.DataFrame:
     # correlation matrix between power/EV/barrel metrics
     cols = [
        'avg_hr_distance',
        'max_hr_distance',
        'avg_launch_speed',
        'max_launch_speed',
        'barrels',
        'brl_percent',
        'hr_count',
        ]
     return df[cols].corr()

def barrel_power_table(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    # table showing relationship between barrel metrics and HR distance
    cols = [
        'player_name',
        'hr_count',
        'avg_hr_distance',
        'max_hr_distance',
        'avg_launch_speed',
        'barrels',
        'brl_percent',
    ]
    subset = df[cols].sort_values('brl_percent', ascending=False)
    return subset.head(n)

def workload_vs_distance(df: pd.DataFrame) -> pd.DataFrame:
    # table of workload (HR count) vs average HR distance

    return df[["player_name", "hr_count", "avg_hr_distance"]]

def find_outliers(df: pd.DataFrame, 
                  columns: Iterable[str] = ('avg_hr_distance', 'max_hr_distance', 'avg_launch_speed'),
                  z_thresh: float = 2.5,
                  ) -> pd.DataFrame:
    out_df = df.copy()
    for col in columns:
        mean = out_df[col].mean()
        std = out_df[col].std(ddof=0)
        if std == 0:
            out_df[f"{col}_z"] = 0.0
        else:
            out_df[f"{col}_z"] = (out_df[col] - mean) / std

    z_cols = [f"{c}_z" for c in columns]
    mask = (out_df[z_cols].abs() > z_thresh).any(axis=1)

    return out_df[mask].sort_values("avg_hr_distance", ascending=False)

def plot_max_vs_avg_distance(df: pd.DataFrame):
    fig, ax = plt.subplots()
    ax.scatter(df['avg_hr_distance'], df['max_hr_distance'])
    ax.set_xlabel('Average HR Distance')
    ax.set_ylabel('Max HR Distance')
    ax.set_title('Max vs Average HR Distance')
    return fig

def plot_launch_speed_vs_distance(df: pd.DataFrame):
    fig, ax = plt.subplots()
    ax.scatter(df['avg_launch_speed'], df['avg_hr_distance'])
    ax.set_xlabel('Average Launch Speed (Exit Velocity)')
    ax.set_ylabel('Average HR Distance')
    ax.set_title('Exit Velocity vs Average HR Distance')
    return fig

def plot_barrel_percent_vs_distance(df: pd.DataFrame):
    fig, ax = plt.subplots()
    ax.scatter(df['brl_percent'], df['avg_hr_distance'])
    ax.set_xlabel('Barrel Percent')
    ax.set_ylabel('Average HR Distance')
    ax.set_title('Barrel Percent vs Average HR Distance')
    return fig

def plot_hr_count_vs_distance(df: pd.DataFrame):
    # HR count (workload) vs avg HR distance
    fig, ax = plt.subplots()
    ax.scatter(df['hr_count'], df['avg_hr_distance'])
    ax.set_xlabel('Home Run Count')
    ax.set_ylabel('Average HR Distance')
    ax.set_title('Workload vs Average HR Distance')
    return fig

