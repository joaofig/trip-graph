import numpy as np
import pandas as pd

from typing import List

from geo.math import num_haversine, vec_haversine


# Both methods below were taken from
# https://medium.com/unit8-machine-learning-publication/
# from-pandas-wan-to-pandas-master-4860cf0ce442

def mem_usage(df: pd.DataFrame) -> str:
    """
    This method styles the memory usage of a DataFrame to be readable as MB.
    Parameters
    ----------
    df: pd.DataFrame
        Data frame to measure.
    Returns
    -------
    str
        Complete memory usage as a string formatted for MB.
    """
    return f'{df.memory_usage(deep=True).sum() / 1024 ** 2 : 3.2f} MB'


def categorize_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    return df.copy(deep=True).astype({col: 'category' for col in columns})


# This function is here only for reference. When used with the Dublin Bus
# dataset it managed to convert all columns to the category type...
def convert_df(df: pd.DataFrame, deep_copy: bool = True) -> pd.DataFrame:
    """
    Automatically converts columns that are worth stored as
    ``categorical`` dtype.
    Parameters
    ----------
    df: pd.DataFrame
        Data frame to convert.
    deep_copy: bool
        Whether or not to perform a deep copy of the original data frame.
    Returns
    -------
    pd.DataFrame
        Optimized copy of the input data frame.
    """
    return df.copy(deep=deep_copy).astype({
        col: 'category' for col in df.columns
        if df[col].nunique() / df[col].shape[0] < 0.5})


class DataEnhancer(object):
    """
    Specialized data enhancer fot the Vehicle Energy Dataset.
    """

    def __init__(self,
                 ts_col: str = "Timestamp(ms)",
                 lat_col: str = "Latitude[deg]",
                 lon_col: str = "Longitude[deg]",
                 dx_col: str = "dx",
                 dt_col: str = "dt",
                 speed_col: str = "v",
                 one_second: float = 1000.0):
        self.ts_col = ts_col
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.dx_col = dx_col
        self.dt_col = dt_col
        self.speed_col = speed_col
        self.one_second = one_second

    def calculate_dt(self,
                     df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the consecutive duration in seconds.
        :param df: Input DataFrame
        :return: DataFrame with added 'dt' column.
        """
        df[self.dt_col] = df[self.ts_col].diff()
        df[self.dt_col] = df[self.dt_col].fillna(value=0.0)
        df[self.dt_col] = df[self.dt_col] / self.one_second
        return df

    def calculate_dx(self,
                     df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the consecutive distance in meters.
        :param df: Input DataFrame
        :return: DataFrame with added 'dx' column.
        """
        lat0 = df[self.lat_col][:-1].to_numpy()
        lon0 = df[self.lon_col][:-1].to_numpy()
        lat1 = df[self.lat_col][1:].to_numpy()
        lon1 = df[self.lon_col][1:].to_numpy()
        dist = vec_haversine(lat0, lon0, lat1, lon1)
        df[self.dx_col] = np.insert(dist, 0, 0.0)
        return df

    def get_max_speed(self, df: pd.DataFrame) -> float:
        """
        Calculates the maximum speed using the Tukey box plot algorithm
        :param df: Source DataFrame
        :return: Speed at the top whisker of the box plot
        """
        q = df[self.speed_col].quantile([.25, .5, .75])
        iqr = q.loc[0.75] - q.loc[0.25]
        return q.loc[0.75] + 1.5 * iqr

    def calculate_speed(self,
                        df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the consecutive average speeds in km/h.
        :param df: Input DataFrame
        :return: DataFrame with added 'v' column.
        """
        dx = df[self.dx_col].to_numpy()
        dt = df[self.dt_col].to_numpy()
        v = np.zeros_like(dx)
        zi = dt > 0
        v[zi] = dx[zi] / dt[zi] * 3.6
        df[self.speed_col] = v
        return df
