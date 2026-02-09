import pandas as pd

from typing import Iterable

from my_utils.my_consts import ATTRIBUTES

def chunk_grouped_data_extraction(chunks: pd.io.parsers.readers.TextFileReader) -> Iterable[pd.DataFrame]:
    """
    Извлечение промежуточных значений группировки
    :param chunks: список чанков из оригинального датафрейма
    :type chunks: pd.io.parsers.readers.TextFileReader
    :return: два датафрейма с промежуточными метриками
    :rtype: Iterable[DataFrame]
    """
    
    for chunk in chunks:
        # Чтобы функции работали корректно
        chunk['departure'] = pd.to_datetime(chunk['departure'])

        # Группировки для ежедневных и ежемесячных метрик
        daily_group = [chunk.departure.dt.to_period('M'), chunk.departure.dt.day]
        monthly_group = daily_group[0]

        # Данные из чанка
        chunk_metrics_daily = chunk.groupby(daily_group).agg(**ATTRIBUTES)
        chunk_metrics_monthly = chunk.groupby(monthly_group).agg(**ATTRIBUTES)
        
        # Создание общих датафреймов
        if 'df_daily' not in locals():
            df_daily = chunk_metrics_daily
            df_monthly = chunk_metrics_monthly
        else:
            df_daily = df_daily.add(chunk_metrics_daily, fill_value=0)
            df_monthly = df_monthly.add(chunk_metrics_monthly, fill_value=0)
    
    
    return df_daily, df_monthly