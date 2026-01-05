import polars as pl

from src.consts import columns

def reading(path: str):
    df = pl.read_csv(path, try_parse_dates=True, new_columns=columns)
    return df.sort(by="date") 


def preparation(df: pl.DataFrame):
    """
    Docstring for preparation
    
    :param df: input dataframe with logs
    :type df: pl.DataFrame
    """
    # добавление новой колонки дат из существующего unix формата
    df = df.with_columns(pl.from_epoch(pl.col("date"), time_unit="s").alias("date_from_unix"))
    return df