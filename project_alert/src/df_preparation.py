import polars as pl


def reading(path: str):
    df = pl.read_csv(path)
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